"""
Overdue Contributions Report

Shows obligations with status = Overdue.
Columns: Member | Category | Cycle | Due Date | Grace End | Outstanding | Days Overdue
Filters: chama (reqd), member, date range (grace_end_date)
"""

import frappe
from frappe.utils import flt, getdate, nowdate
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
        {"label": "Grace End", "fieldname": "grace_end_date", "fieldtype": "Date", "width": 100},
        {"label": "Outstanding", "fieldname": "amount_outstanding", "fieldtype": "Currency", "width": 120},
        {"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
    ]


def get_data(filters):
    chama = filters.get("chama")
    conditions = "ob.chama = %(chama)s AND ob.status = 'Overdue'"
    params = {"chama": chama}

    if filters.get("member"):
        conditions += " AND ob.member = %(member)s"
        params["member"] = filters["member"]
    if filters.get("from_date"):
        conditions += " AND ob.grace_end_date >= %(from_date)s"
        params["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND ob.grace_end_date <= %(to_date)s"
        params["to_date"] = filters["to_date"]

    today = str(nowdate())

    rows = frappe.db.sql(
        f"""
        SELECT
            ob.name,
            mb.full_name AS member_name,
            cat.category_name,
            ob.cycle,
            ob.due_date,
            ob.grace_end_date,
            ob.amount_outstanding,
            DATEDIFF(%(today)s, ob.grace_end_date) AS days_overdue
        FROM `tabChama Contribution Obligation` ob
        LEFT JOIN `tabChama Member` mb ON mb.name = ob.member
        LEFT JOIN `tabChama Contribution Category` cat ON cat.name = ob.contribution_category
        WHERE {conditions}
        ORDER BY days_overdue DESC, mb.full_name ASC
        """,
        {**params, "today": today},
        as_dict=True,
    )
    return rows
