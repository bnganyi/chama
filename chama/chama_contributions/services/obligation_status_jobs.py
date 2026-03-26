"""
Obligation Status Jobs — daily scheduler jobs for transitioning obligation statuses.

Entry points (all daily):
    refresh_due_statuses      — Pending → Due when due_date <= today
    refresh_overdue_statuses  — Due / Partially Paid → Overdue when grace_end_date < today
    apply_penalties_skeleton  — logs candidates; no obligation creation in v1

Terminal statuses (Paid, Waived, Cancelled) are never touched.
"""

import frappe
from frappe.utils import getdate, nowdate


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
        fields=["name"],
        limit_page_length=0,
    )

    count = 0
    for ob in obligations:
        frappe.db.set_value(
            "Chama Contribution Obligation", ob.name, "status", "Due", update_modified=False
        )
        count += 1

    if count:
        frappe.db.commit()
        frappe.logger().info(f"refresh_due_statuses: {count} obligations moved to Due")

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
        fields=["name"],
        limit_page_length=0,
    )

    count = 0
    for ob in obligations:
        frappe.db.set_value(
            "Chama Contribution Obligation", ob.name, "status", "Overdue", update_modified=False
        )
        count += 1

    if count:
        frappe.db.commit()
        frappe.logger().info(f"refresh_overdue_statuses: {count} obligations moved to Overdue")

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
