"""
Allocation Engine — core financial logic for distributing payments against obligations.

Rules:
- Oldest-first ordering by due_date (Overdue first, then Due, then Partially Paid).
- Never allow amount_paid + amount_waived > amount_due on any obligation.
- Payment status → Allocated if fully consumed, Partially Allocated if remainder remains.
- No wallet / credit carried over; any unallocated remainder stays with the payment.
- All DB mutations happen within the caller's transaction; no explicit commit here.

Payment Status State Machine
-----------------------------
Valid transitions (enforced by this engine):

    Recorded ──► Allocated          (payment fully consumed by obligations)
    Recorded ──► Partially Allocated (payment partially consumed)
    Recorded ──► Flagged            (duplicate reference detected — set by Payment controller)
    Allocated ──► Reversed          (all allocations unwound)
    Partially Allocated ──► Reversed

Blocked transitions:
    Allocated → Allocated           (re-allocation of a fully allocated payment is forbidden)
    Flagged → Allocated             (flagged payments must be reviewed before allocation)
    Reversed → *                    (Reversed is terminal; re-allocation is forbidden)

See also: OBLIGATION_STATUS_MACHINE in chama_contribution_obligation.py
"""

import json

import frappe
from frappe.utils import flt, now_datetime


OPEN_STATUSES = ("Due", "Overdue", "Partially Paid", "Pending")

STATUS_PRIORITY = {
    "Overdue": 0,
    "Due": 1,
    "Partially Paid": 2,
    "Pending": 3,
}

# Payments in these statuses cannot be (re-)allocated.
PAYMENT_BLOCKED_STATUSES = ("Reversed", "Allocated", "Flagged")


def _create_audit_log(chama, event_type, actor, doc_type, doc_name, summary, before_state=None, after_state=None):
    """
    Insert one immutable Chama Audit Log record.

    Failures are swallowed and logged so that an audit-log write error never
    blocks a financial transaction.
    """
    try:
        frappe.get_doc({
            "doctype": "Chama Audit Log",
            "chama": chama,
            "event_type": event_type,
            "actor": actor or frappe.session.user,
            "timestamp": now_datetime(),
            "document_type": doc_type,
            "document_name": doc_name,
            "summary": summary,
            "before_state": json.dumps(before_state, default=str) if before_state else None,
            "after_state": json.dumps(after_state, default=str) if after_state else None,
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Audit log failed: {event_type} / {doc_name}")


def get_open_obligations(chama, member, target_category=None, allow_future=False):
    """
    Return open obligations for a member in a chama, ordered oldest-first.

    Args:
        chama (str): Chama docname.
        member (str): Chama Member docname.
        target_category (str|None): Filter to a specific contribution category.
        allow_future (bool): Include Pending obligations whose due_date is in the future.

    Returns:
        list[dict]: Obligation field dicts ordered by priority then due_date.
    """
    filters = {
        "chama": chama,
        "member": member,
        "status": ("in", list(OPEN_STATUSES)),
    }
    if target_category:
        filters["contribution_category"] = target_category

    obligations = frappe.get_all(
        "Chama Contribution Obligation",
        filters=filters,
        fields=[
            "name",
            "amount_due",
            "amount_paid",
            "amount_waived",
            "amount_outstanding",
            "due_date",
            "status",
            "contribution_category",
        ],
        order_by="due_date asc",
    )

    if not allow_future:
        today = frappe.utils.today()
        obligations = [o for o in obligations if not o.due_date or str(o.due_date) <= str(today)]

    obligations.sort(key=lambda o: (STATUS_PRIORITY.get(o.status, 99), str(o.due_date or "")))
    return obligations


def recompute_obligation_amounts_and_status(obligation_doc):
    """
    Recalculate amount_outstanding and derive status from raw amounts.

    Terminal statuses (Cancelled, Waived) are never modified.
    """
    if obligation_doc.status in ("Cancelled", "Waived"):
        return

    paid = flt(obligation_doc.amount_paid)
    waived = flt(obligation_doc.amount_waived)
    due = flt(obligation_doc.amount_due)

    outstanding = max(due - paid - waived, 0)
    obligation_doc.amount_outstanding = outstanding

    if paid + waived >= due:
        obligation_doc.status = "Paid"
    elif paid > 0:
        obligation_doc.status = "Partially Paid"

    obligation_doc.save(ignore_permissions=True)


def allocate_payment(payment_name, target_category=None, allow_future=False):
    """
    Allocate a recorded payment against the member's open obligations.

    Creates child allocation rows on the payment, updates obligation amounts,
    and sets the final payment status.

    Args:
        payment_name (str): Name of the Chama Contribution Payment document.
        target_category (str|None): Restrict allocation to one category.
        allow_future (bool): Allow allocation to future (Pending) obligations.

    Returns:
        dict: Summary with keys allocated_total, rows_created, payment_status.
    """
    payment = frappe.get_doc("Chama Contribution Payment", payment_name)

    if payment.status in PAYMENT_BLOCKED_STATUSES:
        frappe.throw(
            f"Payment {payment_name} has status '{payment.status}' and cannot be allocated. "
            f"Blocked statuses: {', '.join(PAYMENT_BLOCKED_STATUSES)}.",
            frappe.ValidationError,
        )

    obligations = get_open_obligations(
        payment.chama, payment.member, target_category=target_category, allow_future=allow_future
    )

    status_before = payment.status
    remaining = flt(payment.amount_received)
    rows_created = 0
    allocated_total = 0.0

    payment.allocations = []

    for idx, ob in enumerate(obligations, start=1):
        if remaining <= 0:
            break

        ob_doc = frappe.get_doc("Chama Contribution Obligation", ob.name)
        available = flt(ob_doc.amount_outstanding)
        if available <= 0:
            continue

        apply_amount = min(remaining, available)

        ob_doc.amount_paid = flt(ob_doc.amount_paid) + apply_amount
        recompute_obligation_amounts_and_status(ob_doc)

        alloc_type = "Overdue" if ob_doc.status in ("Overdue",) else "Due"
        payment.append(
            "allocations",
            {
                "obligation": ob.name,
                "contribution_category": ob.contribution_category,
                "allocated_amount": apply_amount,
                "allocation_order": idx,
                "allocation_type": alloc_type,
            },
        )

        remaining -= apply_amount
        allocated_total += apply_amount
        rows_created += 1

    if remaining <= 0:
        payment.status = "Allocated"
    elif allocated_total > 0:
        payment.status = "Partially Allocated"

    payment.save(ignore_permissions=True)

    result = {
        "allocated_total": allocated_total,
        "rows_created": rows_created,
        "payment_status": payment.status,
        "unallocated_remainder": remaining,
    }

    _create_audit_log(
        chama=payment.chama,
        event_type="Payment Allocated",
        actor=frappe.session.user,
        doc_type="Chama Contribution Payment",
        doc_name=payment_name,
        summary=(
            f"Allocated {allocated_total:.2f} across {rows_created} obligation(s). "
            f"Payment status: {payment.status}. Unallocated remainder: {remaining:.2f}."
        ),
        before_state={"status": status_before},
        after_state=result,
    )

    return result


def reverse_payment_allocations(payment_name):
    """
    Reverse all allocations for a payment: subtract amounts from obligations,
    clear child rows, and set payment status to Reversed.

    Args:
        payment_name (str): Name of the Chama Contribution Payment document.

    Returns:
        dict: Summary with keys reversed_rows, payment_status.
    """
    payment = frappe.get_doc("Chama Contribution Payment", payment_name)

    if payment.status == "Reversed":
        frappe.throw(f"Payment {payment_name} is already reversed.")

    reversed_rows = 0
    for row in payment.allocations:
        ob_doc = frappe.get_doc("Chama Contribution Obligation", row.obligation)

        if ob_doc.status in ("Cancelled", "Waived"):
            continue

        ob_doc.amount_paid = max(flt(ob_doc.amount_paid) - flt(row.allocated_amount), 0)
        recompute_obligation_amounts_and_status(ob_doc)
        reversed_rows += 1

    status_before = payment.status

    payment.allocations = []
    payment.status = "Reversed"
    payment.save(ignore_permissions=True)

    result = {
        "reversed_rows": reversed_rows,
        "payment_status": payment.status,
    }

    _create_audit_log(
        chama=payment.chama,
        event_type="Payment Reversed",
        actor=frappe.session.user,
        doc_type="Chama Contribution Payment",
        doc_name=payment_name,
        summary=(
            f"Reversed {reversed_rows} allocation row(s). "
            f"Payment status changed from {status_before} to Reversed."
        ),
        before_state={"status": status_before},
        after_state=result,
    )

    return result
