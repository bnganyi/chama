"""
Member Contribution Statement Report

Shows all obligations and corresponding payments for a specific member.
Columns: Cycle | Category | Due Date | Amount Due | Paid | Waived | Outstanding | Status
Filters: chama (reqd), member (reqd), cycle, category
"""

import frappe
from frappe.utils import flt
from chama.chama_core.services.permissions import (
    user_can_access_chama,
    get_chama_member_for_user,
    user_has_chama_role,
    PLATFORM_ADMIN_ROLE,
)


PRIVILEGED_ROLES = {"Chair", "Treasurer", "Auditor"}


def execute(filters=None):
    filters = filters or {}
    validate_access(filters)
    columns = get_columns()
    data, summary = get_data(filters)
    return columns, data, None, summary


def validate_access(filters):
    chama = filters.get("chama")
    member = filters.get("member")

    if not chama:
        frappe.throw("Chama filter is required.")
    if not member:
        frappe.throw("Member filter is required.")
    if not user_can_access_chama(frappe.session.user, chama):
        frappe.throw("You do not have access to this Chama.")

    user = frappe.session.user
    if PLATFORM_ADMIN_ROLE not in frappe.get_roles(user):
        caller = get_chama_member_for_user(user, chama)
        caller_name = getattr(caller, "name", caller) if caller else None
        is_self = caller_name and caller_name == member
        is_privileged = any(user_has_chama_role(user, chama, role) for role in PRIVILEGED_ROLES)
        if not is_self and not is_privileged:
            frappe.throw("You are not authorised to view this member's statement.")


def get_columns():
    return [
        {"label": "Obligation", "fieldname": "name", "fieldtype": "Link", "options": "Chama Contribution Obligation", "width": 120},
        {"label": "Cycle", "fieldname": "cycle", "fieldtype": "Link", "options": "Chama Contribution Cycle", "width": 140},
        {"label": "Category", "fieldname": "category_name", "fieldtype": "Data", "width": 140},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": "Grace End", "fieldname": "grace_end_date", "fieldtype": "Date", "width": 100},
        {"label": "Amount Due", "fieldname": "amount_due", "fieldtype": "Currency", "width": 110},
        {"label": "Amount Paid", "fieldname": "amount_paid", "fieldtype": "Currency", "width": 110},
        {"label": "Amount Waived", "fieldname": "amount_waived", "fieldtype": "Currency", "width": 110},
        {"label": "Outstanding", "fieldname": "amount_outstanding", "fieldtype": "Currency", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]


def get_data(filters):
    chama = filters.get("chama")
    member = filters.get("member")
    conditions = "ob.chama = %(chama)s AND ob.member = %(member)s"
    params = {"chama": chama, "member": member}

    if filters.get("cycle"):
        conditions += " AND ob.cycle = %(cycle)s"
        params["cycle"] = filters["cycle"]
    if filters.get("category"):
        conditions += " AND ob.contribution_category = %(category)s"
        params["category"] = filters["category"]

    rows = frappe.db.sql(
        f"""
        SELECT
            ob.name,
            ob.cycle,
            cat.category_name,
            ob.due_date,
            ob.grace_end_date,
            ob.amount_due,
            ob.amount_paid,
            ob.amount_waived,
            ob.amount_outstanding,
            ob.status
        FROM `tabChama Contribution Obligation` ob
        LEFT JOIN `tabChama Contribution Category` cat ON cat.name = ob.contribution_category
        WHERE {conditions}
        ORDER BY ob.due_date ASC
        """,
        params,
        as_dict=True,
    )

    summary = {
        "total_due": sum(flt(r.amount_due) for r in rows),
        "total_paid": sum(flt(r.amount_paid) for r in rows),
        "total_waived": sum(flt(r.amount_waived) for r in rows),
        "total_outstanding": sum(flt(r.amount_outstanding) for r in rows),
    }

    return rows, summary
