"""
Contribution Compliance Report

Columns: Member | Category | Cycle | Amount Due | Paid | Waived | Outstanding | Status
Filters: chama (reqd), category, cycle, status
"""

import frappe
from frappe.utils import flt
from chama.chama_core.services.permissions import user_can_access_chama


def execute(filters=None):
    filters = filters or {}
    validate_access(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def validate_access(filters):
    chama = filters.get("chama")
    if not chama:
        frappe.throw("Chama filter is required.")
    if not user_can_access_chama(frappe.session.user, chama):
        frappe.throw("You do not have access to this Chama.")


def get_columns():
    return [
        {"label": "Obligation", "fieldname": "name", "fieldtype": "Link", "options": "Chama Contribution Obligation", "width": 120},
        {"label": "Member", "fieldname": "member_name", "fieldtype": "Data", "width": 160},
        {"label": "Category", "fieldname": "category_name", "fieldtype": "Data", "width": 140},
        {"label": "Cycle", "fieldname": "cycle", "fieldtype": "Link", "options": "Chama Contribution Cycle", "width": 140},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": "Amount Due", "fieldname": "amount_due", "fieldtype": "Currency", "width": 110},
        {"label": "Amount Paid", "fieldname": "amount_paid", "fieldtype": "Currency", "width": 110},
        {"label": "Amount Waived", "fieldname": "amount_waived", "fieldtype": "Currency", "width": 110},
        {"label": "Outstanding", "fieldname": "amount_outstanding", "fieldtype": "Currency", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]


def get_data(filters):
    chama = filters.get("chama")
    conditions = "ob.chama = %(chama)s"
    params = {"chama": chama}

    if filters.get("category"):
        conditions += " AND ob.contribution_category = %(category)s"
        params["category"] = filters["category"]
    if filters.get("cycle"):
        conditions += " AND ob.cycle = %(cycle)s"
        params["cycle"] = filters["cycle"]
    if filters.get("status"):
        conditions += " AND ob.status = %(status)s"
        params["status"] = filters["status"]

    rows = frappe.db.sql(
        f"""
        SELECT
            ob.name,
            mb.full_name AS member_name,
            cat.category_name,
            ob.cycle,
            ob.due_date,
            ob.amount_due,
            ob.amount_paid,
            ob.amount_waived,
            ob.amount_outstanding,
            ob.status
        FROM `tabChama Contribution Obligation` ob
        LEFT JOIN `tabChama Member` mb ON mb.name = ob.member
        LEFT JOIN `tabChama Contribution Category` cat ON cat.name = ob.contribution_category
        WHERE {conditions}
        ORDER BY ob.due_date ASC, mb.full_name ASC
        """,
        params,
        as_dict=True,
    )
    return rows
