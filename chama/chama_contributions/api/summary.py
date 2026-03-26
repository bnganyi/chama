"""
Member Contribution Summary API — B-010

Access rules:
- A member may only read their own summary.
- Chair, Treasurer, and Auditor may read any member's summary within their Chama.
"""

import frappe
from frappe.utils import flt
from chama.chama_core.api.responses import success_response, error_response
from chama.chama_core.services.permissions import (
    user_can_access_chama,
    get_chama_member_for_user,
    user_has_chama_role,
    PLATFORM_ADMIN_ROLE,
)


PRIVILEGED_ROLES = {"Chair", "Treasurer", "Auditor"}


@frappe.whitelist()
def get_member_contribution_summary(chama, member, cycle=None, category=None):
    """
    Return a contribution summary for a member within a Chama.

    Args:
        chama (str): Chama docname.
        member (str): Chama Member docname.
        cycle (str|None): Optional filter to a specific cycle.
        category (str|None): Optional filter to a specific contribution category.

    Returns:
        dict: Standard success response with summary data, or error response.
    """
    user = frappe.session.user

    if not user or user == "Guest":
        return error_response("UNAUTHORIZED", "Authentication required.")

    if not user_can_access_chama(user, chama):
        return error_response("ACCESS_DENIED", f"You do not have access to Chama {chama}.")

    # Platform admins bypass member-level access checks
    if PLATFORM_ADMIN_ROLE not in frappe.get_roles(user):
        caller_member = get_chama_member_for_user(user, chama)
        # compare by name (caller_member may be a Document)
        caller_member_name = getattr(caller_member, "name", caller_member) if caller_member else None
        is_self = caller_member_name and caller_member_name == member
        is_privileged = any(user_has_chama_role(user, chama, role) for role in PRIVILEGED_ROLES)
        if not is_self and not is_privileged:
            return error_response("FORBIDDEN", "You are not authorised to view this member's contribution summary.")

    filters = {"chama": chama, "member": member}
    if cycle:
        filters["cycle"] = cycle
    if category:
        filters["contribution_category"] = category

    obligations = frappe.get_all(
        "Chama Contribution Obligation",
        filters=filters,
        fields=[
            "name",
            "cycle",
            "contribution_category",
            "amount_due",
            "amount_paid",
            "amount_waived",
            "amount_outstanding",
            "due_date",
            "grace_end_date",
            "status",
        ],
        order_by="due_date asc",
    )

    total_due = sum(flt(o.amount_due) for o in obligations)
    total_paid = sum(flt(o.amount_paid) for o in obligations)
    total_waived = sum(flt(o.amount_waived) for o in obligations)
    total_outstanding = sum(flt(o.amount_outstanding) for o in obligations)
    total_overdue = sum(flt(o.amount_outstanding) for o in obligations if o.status == "Overdue")

    return success_response(
        {
            "member": member,
            "chama": chama,
            "total_due": total_due,
            "total_paid": total_paid,
            "total_waived": total_waived,
            "total_outstanding": total_outstanding,
            "total_overdue": total_overdue,
            "obligations": [dict(o) for o in obligations],
        }
    )
