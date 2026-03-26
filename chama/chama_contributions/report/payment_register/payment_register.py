"""
Payment Register Report

Columns: Payment | Member | Date | Amount | Method | Reference | Channel | Status | Duplicate
Filters: chama (reqd), member, date range, payment_method
"""

import frappe
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
        {"label": "Payment", "fieldname": "name", "fieldtype": "Link", "options": "Chama Contribution Payment", "width": 120},
        {"label": "Member", "fieldname": "member_name", "fieldtype": "Data", "width": 160},
        {"label": "Payment Date", "fieldname": "payment_date", "fieldtype": "Datetime", "width": 140},
        {"label": "Amount Received", "fieldname": "amount_received", "fieldtype": "Currency", "width": 130},
        {"label": "Method", "fieldname": "payment_method", "fieldtype": "Data", "width": 120},
        {"label": "Reference", "fieldname": "payment_reference", "fieldtype": "Data", "width": 140},
        {"label": "Channel", "fieldname": "source_channel", "fieldtype": "Data", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Duplicate", "fieldname": "duplicate_flag", "fieldtype": "Check", "width": 80},
    ]


def get_data(filters):
    chama = filters.get("chama")
    conditions = "p.chama = %(chama)s"
    params = {"chama": chama}

    if filters.get("member"):
        conditions += " AND p.member = %(member)s"
        params["member"] = filters["member"]
    if filters.get("from_date"):
        conditions += " AND DATE(p.payment_date) >= %(from_date)s"
        params["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND DATE(p.payment_date) <= %(to_date)s"
        params["to_date"] = filters["to_date"]
    if filters.get("payment_method"):
        conditions += " AND p.payment_method = %(payment_method)s"
        params["payment_method"] = filters["payment_method"]

    rows = frappe.db.sql(
        f"""
        SELECT
            p.name,
            mb.full_name AS member_name,
            p.payment_date,
            p.amount_received,
            p.payment_method,
            p.payment_reference,
            p.source_channel,
            p.status,
            p.duplicate_flag
        FROM `tabChama Contribution Payment` p
        LEFT JOIN `tabChama Member` mb ON mb.name = p.member
        WHERE {conditions}
        ORDER BY p.payment_date DESC
        """,
        params,
        as_dict=True,
    )
    return rows
