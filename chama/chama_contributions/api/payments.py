"""
Payment Submission API — B-009

Validates caller access, creates a Chama Contribution Payment record,
then triggers the allocation engine.
"""

import frappe
from chama.chama_core.api.responses import success_response, error_response, validation_error_response
from chama.chama_core.services.permissions import user_can_access_chama
from chama.chama_core.utils.tenant import ensure_member_matches_chama
from chama.chama_contributions.services.allocation_engine import allocate_payment


@frappe.whitelist()
def submit_payment(
    chama,
    member,
    amount_received,
    payment_method,
    payment_reference=None,
    source_channel="Desk",
    target_category=None,
):
    """
    Create a payment record and allocate it against the member's open obligations.

    Args:
        chama (str): Chama docname.
        member (str): Chama Member docname.
        amount_received (float): Amount received.
        payment_method (str): One of Mobile Money / Cash / Bank / Internal Transfer / Adjustment.
        payment_reference (str|None): External reference (MPesa code, bank ref, etc.).
        source_channel (str): Mobile / Desk / Import / API.
        target_category (str|None): Restrict allocation to one contribution category.

    Returns:
        dict: Standard success or error response.
    """
    user = frappe.session.user

    if not user or user == "Guest":
        return error_response("UNAUTHORIZED", "Authentication required.")

    if not user_can_access_chama(user, chama):
        return error_response("ACCESS_DENIED", f"You do not have access to Chama {chama}.")

    try:
        ensure_member_matches_chama(member, chama)
    except frappe.ValidationError as exc:
        return validation_error_response([{"field": "member", "message": str(exc)}])

    try:
        amount = float(amount_received)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return validation_error_response([{"field": "amount_received", "message": "amount_received must be a positive number."}])

    try:
        payment = frappe.get_doc(
            {
                "doctype": "Chama Contribution Payment",
                "chama": chama,
                "member": member,
                "payment_date": frappe.utils.now_datetime(),
                "amount_received": amount,
                "payment_method": payment_method,
                "payment_reference": payment_reference,
                "source_channel": source_channel,
                "status": "Recorded",
                "entered_by": user,
            }
        )
        payment.insert(ignore_permissions=True)
        frappe.db.commit()
    except frappe.ValidationError as exc:
        return validation_error_response(str(exc))
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "submit_payment: payment creation failed")
        return error_response("PAYMENT_CREATION_FAILED", f"Failed to create payment: {exc}")

    try:
        alloc_result = allocate_payment(payment.name, target_category=target_category)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "submit_payment: allocation failed")
        return success_response(
            {
                "payment": payment.name,
                "allocation_warning": str(exc),
                "status": payment.status,
            }
        )

    return success_response(
        {
            "payment": payment.name,
            "status": alloc_result["payment_status"],
            "allocated_total": alloc_result["allocated_total"],
            "rows_created": alloc_result["rows_created"],
            "unallocated_remainder": alloc_result["unallocated_remainder"],
        }
    )
