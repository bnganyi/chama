"""
Obligation Status Jobs — daily scheduler jobs for transitioning obligation statuses.

Entry points (all daily):
    refresh_due_statuses      — Pending → Due when due_date <= today
    refresh_overdue_statuses  — Due / Partially Paid → Overdue when grace_end_date < today
    apply_penalties_skeleton  — logs candidates; no obligation creation in v1

Terminal statuses (Paid, Waived, Cancelled) are never touched.

Note on frappe.db.set_value usage
-----------------------------------
These jobs use frappe.db.set_value() rather than frappe.get_doc().save() intentionally:
  - Only the `status` field is changed — no financial amounts are touched.
  - Bulk operations over potentially hundreds of obligations per run make per-doc
    saves prohibitively slow (each triggers a full validate() + ORM round-trip).
  - The obligation controller's _compute_status() does not set "Due" or "Overdue";
    those statuses are exclusively owned by this scheduler (see OBLIGATION_STATUS_MACHINE).
  - Using update_modified=False avoids spurious `modified` timestamp churn.

DO NOT copy this pattern into services, APIs, or any code that changes financial
amounts (amount_paid, amount_waived, amount_outstanding). Those must always go
through the allocation engine's recompute_obligation_amounts_and_status().
"""

import frappe
from frappe.utils import getdate, now_datetime, nowdate


TERMINAL_STATUSES = {"Paid", "Waived", "Cancelled"}


def refresh_due_statuses(today_date=None):
    """
    Transition Pending obligations to Due when their due_date has been reached.

    Args:
        today_date (str|None): Override today for testing (YYYY-MM-DD).

    Returns:
        int: Number of obligations updated.
    """
    today = str(today_date or nowdate())

    obligations = frappe.db.get_all(
        "Chama Contribution Obligation",
        filters={"status": "Pending", "due_date": ("<=", today)},
        fields=["name", "chama"],
        limit_page_length=0,
    )

    count = 0
    chama_counts = {}
    for ob in obligations:
        frappe.db.set_value(
            "Chama Contribution Obligation", ob.name, "status", "Due", update_modified=False
        )
        count += 1
        chama_counts[ob.chama] = chama_counts.get(ob.chama, 0) + 1

    if count:
        frappe.db.commit()
        frappe.logger().info(f"refresh_due_statuses: {count} obligations moved to Due")
        _log_status_job_audit(chama_counts, transition="Pending → Due", today=today)

    return count


def refresh_overdue_statuses(today_date=None):
    """
    Transition Due / Partially Paid obligations to Overdue when grace_end_date < today.

    Args:
        today_date (str|None): Override today for testing (YYYY-MM-DD).

    Returns:
        int: Number of obligations updated.
    """
    today = str(today_date or nowdate())

    obligations = frappe.db.get_all(
        "Chama Contribution Obligation",
        filters={
            "status": ("in", ["Due", "Partially Paid"]),
            "grace_end_date": ("<", today),
        },
        fields=["name", "chama"],
        limit_page_length=0,
    )

    count = 0
    chama_counts = {}
    for ob in obligations:
        frappe.db.set_value(
            "Chama Contribution Obligation", ob.name, "status", "Overdue", update_modified=False
        )
        count += 1
        chama_counts[ob.chama] = chama_counts.get(ob.chama, 0) + 1

    if count:
        frappe.db.commit()
        frappe.logger().info(f"refresh_overdue_statuses: {count} obligations moved to Overdue")
        _log_status_job_audit(chama_counts, transition="Due/Partially Paid → Overdue", today=today)

    return count


def apply_penalties_skeleton(today_date=None):
    """
    Skeleton for penalty application (Phase C scope).

    Logs Overdue obligations that are eligible for penalty but does not create
    any Penalty obligation records in v1.

    Args:
        today_date (str|None): Override today for testing.

    Returns:
        list[str]: Names of obligations that are penalty candidates.
    """
    today = str(today_date or nowdate())

    candidates = frappe.db.get_all(
        "Chama Contribution Obligation",
        filters={
            "status": "Overdue",
            "penalty_applied": 0,
            "grace_end_date": ("<", today),
        },
        fields=["name", "chama", "member", "amount_outstanding"],
        limit_page_length=0,
    )

    if candidates:
        frappe.logger().info(
            f"apply_penalties_skeleton: {len(candidates)} overdue obligations are penalty candidates "
            f"(penalty creation deferred to Phase C)"
        )

    return [c.name for c in candidates]


def _log_status_job_audit(chama_counts, transition, today):
    """
    Create one Chama Audit Log entry per chama affected by a status job run.

    One summary record per chama (not per obligation) keeps the audit log
    concise while still providing a per-chama change trail.
    """
    try:
        from chama.chama_contributions.services.allocation_engine import _create_audit_log
        for chama, cnt in chama_counts.items():
            _create_audit_log(
                chama=chama,
                event_type="Obligation Status Changed",
                actor="Administrator",
                doc_type="Chama Contribution Obligation",
                doc_name="(bulk)",
                summary=f"Scheduler: {cnt} obligation(s) transitioned {transition} on {today}.",
                before_state=None,
                after_state={"chama": chama, "count": cnt, "transition": transition, "date": today},
            )
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Audit log failed for status job: {transition}")
