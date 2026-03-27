"""
Chama test seed data — single source of truth for all phase test files.

Each future phase adds its own data definitions here and extends
seed_data() with a seed_phase_{n}() call.

Usage:
    from chama.chama_core.tests.seed import seed_data
    cr, mr, manifest = seed_data()

Registry keys:
    cr  = {"UMOJA": "CH-000X", "HARVEST": "CH-000Y", "JIRANI": "CH-000Z"}
    mr  = {("UMOJA", "+254700100001"): "MB-000X", ...}
"""

import frappe
from frappe.utils import today

# ──────────────────────────────────────────────────────────────────────────────
# Phase A — Foundation seed definitions
# ──────────────────────────────────────────────────────────────────────────────

CHAMA_DEFS = [
    {
        "chama_name": "Umoja Women Investment Group",
        "chama_code": "UMOJA",
        "status": "Active",
        "base_currency": "KES",
        "timezone": "Africa/Nairobi",
        "country": "Kenya",
        "allow_new_member_applications": 1,
    },
    {
        "chama_name": "Harvest Welfare Circle",
        "chama_code": "HARVEST",
        "status": "Active",
        "base_currency": "KES",
        "timezone": "Africa/Nairobi",
        "country": "Kenya",
        "allow_new_member_applications": 1,
    },
    {
        "chama_name": "Jirani Land Pool",
        "chama_code": "JIRANI",
        "status": "Inactive",
        "base_currency": "KES",
        "timezone": "Africa/Nairobi",
        "country": "Kenya",
        "allow_new_member_applications": 0,
    },
]

USER_DEFS = [
    {"email": "grace@umoja.test",            "first_name": "Grace",    "last_name": "Wanjiku"},
    {"email": "samuel@shared.test",          "first_name": "Samuel",   "last_name": "Otieno"},
    {"email": "ann@harvest.test",            "first_name": "Ann",      "last_name": "Wairimu"},
    {"email": "joseph@jirani.test",          "first_name": "Joseph",   "last_name": "Mwangi"},
    {"email": "faith@ops.test",              "first_name": "Faith",    "last_name": "Njeri"},
    {"email": "linda@audit.test",            "first_name": "Linda",    "last_name": "Achieng"},
    {"email": "outsider@none.test",          "first_name": "Outsider", "last_name": "User"},
    {"email": "platform.admin@chama.test",   "first_name": "Platform", "last_name": "Admin"},
]

SETTINGS_DEFS = {
    "UMOJA":   {"budget_overrun_mode": "Warn"},
    "HARVEST": {"budget_overrun_mode": "Block"},
    "JIRANI":  {"budget_overrun_mode": "Allow With Escalation"},
}

MEMBER_DEFS = [
    # Umoja
    {
        "chama_code": "UMOJA", "user": "grace@umoja.test",
        "full_name": "Grace Wanjiku", "phone": "+254700100001",
        "email": "grace@umoja.test", "national_id": "29001111",
        "status": "Active", "join_date": "2024-02-10", "primary_role": "Chair",
    },
    {
        "chama_code": "UMOJA", "user": "samuel@shared.test",
        "full_name": "Samuel Otieno", "phone": "+254700100002",
        "email": "samuel@shared.test", "national_id": "30112233",
        "status": "Active", "join_date": "2024-03-01", "primary_role": "Treasurer",
    },
    {
        "chama_code": "UMOJA", "user": "faith@ops.test",
        "full_name": "Faith Njeri", "phone": "+254700100003",
        "email": "faith@ops.test", "national_id": "31223344",
        "status": "Suspended", "join_date": "2024-05-15", "primary_role": "Member",
        "suspension_reason": "Non-compliance with agreed rules",
    },
    {
        "chama_code": "UMOJA", "user": "linda@audit.test",
        "full_name": "Linda Achieng", "phone": "+254700100004",
        "email": "linda@audit.test", "national_id": "32334455",
        "status": "Active", "join_date": "2024-06-20", "primary_role": "Auditor",
    },
    # Harvest
    {
        "chama_code": "HARVEST", "user": "ann@harvest.test",
        "full_name": "Ann Wairimu", "phone": "+254711200001",
        "email": "ann@harvest.test", "national_id": "33445566",
        "status": "Active", "join_date": "2024-01-12", "primary_role": "Chair",
    },
    {
        "chama_code": "HARVEST", "user": "samuel@shared.test",
        "full_name": "Samuel Otieno", "phone": "+254711200002",
        "email": "samuel@shared.test", "national_id": "30112233",
        "status": "Active", "join_date": "2024-04-05", "primary_role": "Member",
    },
    {
        "chama_code": "HARVEST", "user": "faith@ops.test",
        "full_name": "Faith Njeri", "phone": "+254711200003",
        "email": "faith@ops.test", "national_id": "31223344",
        "status": "Active", "join_date": "2024-07-01", "primary_role": "Secretary",
    },
    # Jirani
    {
        "chama_code": "JIRANI", "user": "joseph@jirani.test",
        "full_name": "Joseph Mwangi", "phone": "+254722300001",
        "email": "joseph@jirani.test", "national_id": "34556677",
        "status": "Dormant", "join_date": "2023-09-10", "primary_role": "Member",
    },
]

ROLE_ASSIGNMENT_DEFS = [
    # Umoja
    {"chama_code": "UMOJA",   "phone": "+254700100001", "role_name": "Chair",     "effective_from": "2024-02-10"},
    {"chama_code": "UMOJA",   "phone": "+254700100002", "role_name": "Treasurer", "effective_from": "2024-03-01"},
    {"chama_code": "UMOJA",   "phone": "+254700100003", "role_name": "Member",    "effective_from": "2024-05-15"},
    {"chama_code": "UMOJA",   "phone": "+254700100004", "role_name": "Auditor",   "effective_from": "2024-06-20"},
    # Harvest
    {"chama_code": "HARVEST", "phone": "+254711200001", "role_name": "Chair",     "effective_from": "2024-01-12"},
    {"chama_code": "HARVEST", "phone": "+254711200002", "role_name": "Member",    "effective_from": "2024-04-05"},
    {"chama_code": "HARVEST", "phone": "+254711200003", "role_name": "Secretary", "effective_from": "2024-07-01"},
    # Jirani
    {"chama_code": "JIRANI",  "phone": "+254722300001", "role_name": "Member",    "effective_from": "2023-09-10"},
]


# ──────────────────────────────────────────────────────────────────────────────
# Seed helpers — idempotent inserts
# ──────────────────────────────────────────────────────────────────────────────

def _log_created(label):  return ("CREATED",  label)
def _log_existing(label): return ("EXISTING", label)


def seed_users(user_defs=None):
    log = []
    for u in (user_defs or USER_DEFS):
        if frappe.db.exists("User", u["email"]):
            log.append(_log_existing(u["email"]))
            continue
        doc = frappe.get_doc({
            "doctype": "User",
            "email": u["email"],
            "first_name": u["first_name"],
            "last_name": u["last_name"],
            "full_name": f"{u['first_name']} {u['last_name']}",
            "enabled": 1,
            "send_welcome_email": 0,
            "new_password": "Test@1234!",
        })
        doc.insert(ignore_permissions=True)
        log.append(_log_created(u["email"]))
    frappe.db.commit()
    return log


def seed_chamas(chama_defs=None):
    """Returns (registry, log). registry = {"UMOJA": "CH-000X", ...}"""
    registry = {}
    log = []
    for cd in (chama_defs or CHAMA_DEFS):
        existing = frappe.db.get_value("Chama", {"chama_code": cd["chama_code"]}, "name")
        if existing:
            registry[cd["chama_code"]] = existing
            log.append(_log_existing(f"{cd['chama_code']} → {existing}"))
            continue
        doc = frappe.get_doc({"doctype": "Chama", **cd})
        doc.insert(ignore_permissions=True)
        registry[cd["chama_code"]] = doc.name
        log.append(_log_created(f"{cd['chama_code']} → {doc.name}"))
    frappe.db.commit()
    return registry, log


def seed_settings(chama_registry, settings_defs=None):
    log = []
    for code, cfg in (settings_defs or SETTINGS_DEFS).items():
        chama_name = chama_registry[code]
        if frappe.db.exists("Chama Settings", {"chama": chama_name}):
            log.append(_log_existing(f"Settings for {code}"))
            continue
        doc = frappe.get_doc({"doctype": "Chama Settings", "chama": chama_name, **cfg})
        doc.insert(ignore_permissions=True)
        log.append(_log_created(f"Settings for {code}"))
    frappe.db.commit()
    return log


def seed_members(chama_registry, member_defs=None):
    """Returns (member_registry, log). member_registry = {("UMOJA", "+2547..."): "MB-000X", ...}"""
    member_registry = {}
    log = []
    for md in (member_defs or MEMBER_DEFS):
        chama_name = chama_registry[md["chama_code"]]
        existing = frappe.db.get_value(
            "Chama Member", {"phone": md["phone"], "chama": chama_name}, "name"
        )
        if existing:
            member_registry[(md["chama_code"], md["phone"])] = existing
            log.append(_log_existing(f"{md['full_name']} in {md['chama_code']} → {existing}"))
            continue
        fields = {k: v for k, v in md.items() if k != "chama_code"}
        fields["chama"] = chama_name
        doc = frappe.get_doc({"doctype": "Chama Member", **fields})
        doc.insert(ignore_permissions=True)
        member_registry[(md["chama_code"], md["phone"])] = doc.name
        log.append(_log_created(f"{md['full_name']} in {md['chama_code']} → {doc.name}"))
    frappe.db.commit()
    return member_registry, log


def seed_role_assignments(chama_registry, member_registry, role_defs=None):
    log = []
    for rd in (role_defs or ROLE_ASSIGNMENT_DEFS):
        member_name = member_registry[(rd["chama_code"], rd["phone"])]
        chama_name  = chama_registry[rd["chama_code"]]
        existing = frappe.db.get_value(
            "Chama Member Role Assignment",
            {"member": member_name, "role_name": rd["role_name"], "chama": chama_name},
            "name",
        )
        if existing:
            log.append(_log_existing(f"{member_name} → {rd['role_name']} in {rd['chama_code']}"))
            continue
        doc = frappe.get_doc({
            "doctype": "Chama Member Role Assignment",
            "chama": chama_name,
            "member": member_name,
            "role_name": rd["role_name"],
            "effective_from": rd["effective_from"],
            "active": 1,
            "assigned_by": "Administrator",
        })
        doc.insert(ignore_permissions=True)
        log.append(_log_created(f"{member_name} → {rd['role_name']} in {rd['chama_code']}"))
    frappe.db.commit()
    return log


def seed_data():
    """
    Seed all test data idempotently (Phase A + Phase B).

    Returns:
        tuple: (chama_registry, member_registry, manifest)
            chama_registry  = {"UMOJA": "CH-000X", ...}
            member_registry = {("UMOJA", "+2547..."): "MB-000X", ...}
            manifest        = {"users": [...], "chamas": [...], ...}
    """
    manifest = {}
    manifest["users"] = seed_users()
    cr, manifest["chamas"] = seed_chamas()
    manifest["settings"] = seed_settings(cr)
    mr, manifest["members"] = seed_members(cr)
    manifest["roles"] = seed_role_assignments(cr, mr)
    b_manifest = seed_phase_b(cr, mr)
    manifest.update(b_manifest)
    return cr, mr, manifest


# ──────────────────────────────────────────────────────────────────────────────
# Phase B — Contributions seed definitions
# ──────────────────────────────────────────────────────────────────────────────

# Keys: (chama_code, category_code)
CATEGORY_DEFS = [
    # Umoja
    {
        "chama_code": "UMOJA", "category_code": "SHR",
        "category_name": "Shares", "category_type": "Shares",
        "amount_type": "Fixed", "default_amount": 5000,
        "frequency": "Monthly", "mandatory": 1,
        "allow_partial_payment": 1, "allow_future_prepayment": 0,
        "grace_days": 5, "active": 1, "start_date": "2026-01-01",
    },
    {
        "chama_code": "UMOJA", "category_code": "WLF",
        "category_name": "Welfare Fund", "category_type": "Welfare",
        "amount_type": "Fixed", "default_amount": 1000,
        "frequency": "Monthly", "mandatory": 1,
        "allow_partial_payment": 1, "allow_future_prepayment": 0,
        "grace_days": 3, "active": 1, "start_date": "2026-01-01",
    },
    {
        "chama_code": "UMOJA", "category_code": "EMG",
        "category_name": "Emergency Levy", "category_type": "Levy",
        "amount_type": "Fixed", "default_amount": 2000,
        "frequency": "Ad Hoc", "mandatory": 0,
        "allow_partial_payment": 0, "allow_future_prepayment": 0,
        "grace_days": 2, "active": 1, "start_date": "2026-02-01",
    },
    # Harvest
    {
        "chama_code": "HARVEST", "category_code": "SHR",
        "category_name": "Shares", "category_type": "Shares",
        "amount_type": "Fixed", "default_amount": 3000,
        "frequency": "Monthly", "mandatory": 1,
        "allow_partial_payment": 1, "allow_future_prepayment": 0,
        "grace_days": 5, "active": 1, "start_date": "2026-01-01",
    },
    {
        "chama_code": "HARVEST", "category_code": "WLF",
        "category_name": "Welfare", "category_type": "Welfare",
        "amount_type": "Fixed", "default_amount": 500,
        "frequency": "Monthly", "mandatory": 1,
        "allow_partial_payment": 1, "allow_future_prepayment": 0,
        "grace_days": 3, "active": 1, "start_date": "2026-01-01",
    },
]

# Keys: (chama_code, cycle_name)
CYCLE_DEFS = [
    {
        "chama_code": "UMOJA", "cycle_name": "UMOJA-FEB-2026",
        "period_start": "2026-02-01", "period_end": "2026-02-28",
        "frequency": "Monthly", "status": "Generated",
    },
    {
        "chama_code": "UMOJA", "cycle_name": "UMOJA-MAR-2026",
        "period_start": "2026-03-01", "period_end": "2026-03-31",
        "frequency": "Monthly", "status": "Generated",
    },
    {
        "chama_code": "HARVEST", "cycle_name": "HARVEST-MAR-2026",
        "period_start": "2026-03-01", "period_end": "2026-03-31",
        "frequency": "Monthly", "status": "Generated",
    },
]

# Obligation defs — keyed by (chama_code, member_phone, cycle_name, category_code)
# amount_paid / amount_waived are pre-set directly (no allocation engine at seed time).
OBLIGATION_DEFS = [
    # ── Umoja February ──────────────────────────────────────────────────────
    {"chama_code": "UMOJA", "phone": "+254700100001", "cycle_name": "UMOJA-FEB-2026",
     "cat_code": "SHR", "amount_due": 5000, "amount_paid": 5000, "amount_waived": 0,
     "due_date": "2026-02-05", "grace_end_date": "2026-02-10", "status": "Paid"},
    {"chama_code": "UMOJA", "phone": "+254700100001", "cycle_name": "UMOJA-FEB-2026",
     "cat_code": "WLF", "amount_due": 1000, "amount_paid": 1000, "amount_waived": 0,
     "due_date": "2026-02-05", "grace_end_date": "2026-02-08", "status": "Paid"},
    {"chama_code": "UMOJA", "phone": "+254700100002", "cycle_name": "UMOJA-FEB-2026",
     "cat_code": "SHR", "amount_due": 5000, "amount_paid": 3000, "amount_waived": 0,
     "due_date": "2026-02-05", "grace_end_date": "2026-02-10", "status": "Overdue"},
    {"chama_code": "UMOJA", "phone": "+254700100002", "cycle_name": "UMOJA-FEB-2026",
     "cat_code": "WLF", "amount_due": 1000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-02-05", "grace_end_date": "2026-02-08", "status": "Overdue"},
    {"chama_code": "UMOJA", "phone": "+254700100003", "cycle_name": "UMOJA-FEB-2026",
     "cat_code": "SHR", "amount_due": 5000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-02-05", "grace_end_date": "2026-02-10", "status": "Overdue"},
    {"chama_code": "UMOJA", "phone": "+254700100004", "cycle_name": "UMOJA-FEB-2026",
     "cat_code": "WLF", "amount_due": 1000, "amount_paid": 0, "amount_waived": 1000,
     "due_date": "2026-02-05", "grace_end_date": "2026-02-08", "status": "Waived"},
    # ── Umoja March ─────────────────────────────────────────────────────────
    {"chama_code": "UMOJA", "phone": "+254700100001", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "SHR", "amount_due": 5000, "amount_paid": 5000, "amount_waived": 0,
     "due_date": "2026-03-05", "grace_end_date": "2026-03-10", "status": "Paid"},
    {"chama_code": "UMOJA", "phone": "+254700100001", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "WLF", "amount_due": 1000, "amount_paid": 1000, "amount_waived": 0,
     "due_date": "2026-03-05", "grace_end_date": "2026-03-08", "status": "Paid"},
    {"chama_code": "UMOJA", "phone": "+254700100001", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "EMG", "amount_due": 2000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-12", "grace_end_date": "2026-03-14", "status": "Due"},
    {"chama_code": "UMOJA", "phone": "+254700100002", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "SHR", "amount_due": 5000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-05", "grace_end_date": "2026-03-10", "status": "Due"},
    {"chama_code": "UMOJA", "phone": "+254700100002", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "WLF", "amount_due": 1000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-05", "grace_end_date": "2026-03-08", "status": "Due"},
    {"chama_code": "UMOJA", "phone": "+254700100002", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "EMG", "amount_due": 2000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-12", "grace_end_date": "2026-03-14", "status": "Due"},
    {"chama_code": "UMOJA", "phone": "+254700100004", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "SHR", "amount_due": 5000, "amount_paid": 2500, "amount_waived": 0,
     "due_date": "2026-03-05", "grace_end_date": "2026-03-10", "status": "Partially Paid"},
    {"chama_code": "UMOJA", "phone": "+254700100004", "cycle_name": "UMOJA-MAR-2026",
     "cat_code": "WLF", "amount_due": 1000, "amount_paid": 1000, "amount_waived": 0,
     "due_date": "2026-03-05", "grace_end_date": "2026-03-08", "status": "Paid"},
    # ── Harvest March ────────────────────────────────────────────────────────
    {"chama_code": "HARVEST", "phone": "+254711200001", "cycle_name": "HARVEST-MAR-2026",
     "cat_code": "SHR", "amount_due": 3000, "amount_paid": 3000, "amount_waived": 0,
     "due_date": "2026-03-06", "grace_end_date": "2026-03-11", "status": "Paid"},
    {"chama_code": "HARVEST", "phone": "+254711200001", "cycle_name": "HARVEST-MAR-2026",
     "cat_code": "WLF", "amount_due": 500, "amount_paid": 500, "amount_waived": 0,
     "due_date": "2026-03-06", "grace_end_date": "2026-03-09", "status": "Paid"},
    {"chama_code": "HARVEST", "phone": "+254711200002", "cycle_name": "HARVEST-MAR-2026",
     "cat_code": "SHR", "amount_due": 3000, "amount_paid": 1000, "amount_waived": 0,
     "due_date": "2026-03-06", "grace_end_date": "2026-03-11", "status": "Partially Paid"},
    {"chama_code": "HARVEST", "phone": "+254711200002", "cycle_name": "HARVEST-MAR-2026",
     "cat_code": "WLF", "amount_due": 500, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-06", "grace_end_date": "2026-03-09", "status": "Due"},
    {"chama_code": "HARVEST", "phone": "+254711200003", "cycle_name": "HARVEST-MAR-2026",
     "cat_code": "SHR", "amount_due": 3000, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-06", "grace_end_date": "2026-03-11", "status": "Due"},
    {"chama_code": "HARVEST", "phone": "+254711200003", "cycle_name": "HARVEST-MAR-2026",
     "cat_code": "WLF", "amount_due": 500, "amount_paid": 0, "amount_waived": 0,
     "due_date": "2026-03-06", "grace_end_date": "2026-03-09", "status": "Due"},
]

# Payment defs — keyed by (chama_code, member_phone, payment_reference) or date+amount for Cash
# status is seeded as Recorded; allocations are exercised by the test suite.
PAYMENT_DEFS = [
    {"id": "U-001", "chama_code": "UMOJA", "phone": "+254700100001",
     "payment_date": "2026-02-04 09:15:00", "amount_received": 6000,
     "payment_method": "Mobile Money", "payment_reference": "UMOJA-MP-0001", "source_channel": "Desk"},
    {"id": "U-002", "chama_code": "UMOJA", "phone": "+254700100002",
     "payment_date": "2026-02-07 10:20:00", "amount_received": 3000,
     "payment_method": "Bank", "payment_reference": "UMOJA-BK-0001", "source_channel": "Desk"},
    {"id": "U-003", "chama_code": "UMOJA", "phone": "+254700100001",
     "payment_date": "2026-03-04 08:00:00", "amount_received": 6000,
     "payment_method": "Mobile Money", "payment_reference": "UMOJA-MP-0002", "source_channel": "Mobile"},
    {"id": "U-004", "chama_code": "UMOJA", "phone": "+254700100004",
     "payment_date": "2026-03-06 14:10:00", "amount_received": 3500,
     "payment_method": "Cash", "payment_reference": None, "source_channel": "Desk"},
    {"id": "U-005", "chama_code": "UMOJA", "phone": "+254700100002",
     "payment_date": "2026-03-15 11:45:00", "amount_received": 4000,
     "payment_method": "Mobile Money", "payment_reference": "UMOJA-MP-0003", "source_channel": "API"},
    {"id": "U-006", "chama_code": "UMOJA", "phone": "+254700100002",
     "payment_date": "2026-03-15 11:47:00", "amount_received": 4000,
     "payment_method": "Mobile Money", "payment_reference": "UMOJA-MP-0003", "source_channel": "API"},
    {"id": "U-007", "chama_code": "UMOJA", "phone": "+254700100001",
     "payment_date": "2026-03-13 09:30:00", "amount_received": 2000,
     "payment_method": "Mobile Money", "payment_reference": "UMOJA-MP-LEVY-01", "source_channel": "Desk"},
    {"id": "H-001", "chama_code": "HARVEST", "phone": "+254711200001",
     "payment_date": "2026-03-05 09:00:00", "amount_received": 3500,
     "payment_method": "Mobile Money", "payment_reference": "HARVEST-MP-0001", "source_channel": "Desk"},
    {"id": "H-002", "chama_code": "HARVEST", "phone": "+254711200002",
     "payment_date": "2026-03-08 13:00:00", "amount_received": 1000,
     "payment_method": "Bank", "payment_reference": "HARVEST-BK-0001", "source_channel": "Desk"},
]


def seed_categories(chama_registry, cat_defs=None):
    """Returns (cat_registry, log). cat_registry = {("UMOJA", "SHR"): "CCAT-000X", ...}"""
    cat_registry = {}
    log = []
    for cd in (cat_defs or CATEGORY_DEFS):
        chama_name = chama_registry[cd["chama_code"]]
        existing = frappe.db.get_value(
            "Chama Contribution Category",
            {"chama": chama_name, "category_code": cd["category_code"]},
            "name",
        )
        if existing:
            cat_registry[(cd["chama_code"], cd["category_code"])] = existing
            log.append(_log_existing(f"Category {cd['category_code']} in {cd['chama_code']} → {existing}"))
            continue
        fields = {k: v for k, v in cd.items() if k != "chama_code"}
        fields["chama"] = chama_name
        doc = frappe.get_doc({"doctype": "Chama Contribution Category", **fields})
        doc.insert(ignore_permissions=True)
        cat_registry[(cd["chama_code"], cd["category_code"])] = doc.name
        log.append(_log_created(f"Category {cd['category_code']} in {cd['chama_code']} → {doc.name}"))
    frappe.db.commit()
    return cat_registry, log


def seed_cycles(chama_registry, cycle_defs=None):
    """Returns (cycle_registry, log). cycle_registry = {("UMOJA", "UMOJA-FEB-2026"): "CYC-000X", ...}"""
    cycle_registry = {}
    log = []
    for cd in (cycle_defs or CYCLE_DEFS):
        chama_name = chama_registry[cd["chama_code"]]
        existing = frappe.db.get_value(
            "Chama Contribution Cycle",
            {"chama": chama_name, "cycle_name": cd["cycle_name"]},
            "name",
        )
        if existing:
            cycle_registry[(cd["chama_code"], cd["cycle_name"])] = existing
            log.append(_log_existing(f"Cycle {cd['cycle_name']} → {existing}"))
            continue
        fields = {k: v for k, v in cd.items() if k != "chama_code"}
        fields["chama"] = chama_name
        doc = frappe.get_doc({"doctype": "Chama Contribution Cycle", **fields})
        doc.insert(ignore_permissions=True)
        cycle_registry[(cd["chama_code"], cd["cycle_name"])] = doc.name
        log.append(_log_created(f"Cycle {cd['cycle_name']} → {doc.name}"))
    frappe.db.commit()
    return cycle_registry, log


def seed_obligations(chama_registry, member_registry, cat_registry, cycle_registry, ob_defs=None):
    """Returns (obligation_registry, log). obligation_registry = {(chama_code, phone, cycle_name, cat_code): "COB-000X", ...}"""
    ob_registry = {}
    log = []
    for od in (ob_defs or OBLIGATION_DEFS):
        chama_name = chama_registry[od["chama_code"]]
        member_name = member_registry.get((od["chama_code"], od["phone"]))
        cat_name = cat_registry.get((od["chama_code"], od["cat_code"]))
        cycle_name = cycle_registry.get((od["chama_code"], od["cycle_name"]))

        if not member_name or not cat_name or not cycle_name:
            log.append(("SKIPPED", f"Missing refs for {od['chama_code']} {od['phone']} {od['cycle_name']} {od['cat_code']}"))
            continue

        key = (od["chama_code"], od["phone"], od["cycle_name"], od["cat_code"])
        existing = frappe.db.get_value(
            "Chama Contribution Obligation",
            {"chama": chama_name, "member": member_name, "cycle": cycle_name, "contribution_category": cat_name},
            "name",
        )
        if existing:
            ob_registry[key] = existing
            log.append(_log_existing(f"Obligation {key} → {existing}"))
            continue

        outstanding = max(od["amount_due"] - od["amount_paid"] - od["amount_waived"], 0)
        doc = frappe.get_doc({
            "doctype": "Chama Contribution Obligation",
            "chama": chama_name,
            "member": member_name,
            "cycle": cycle_name,
            "contribution_category": cat_name,
            "amount_due": od["amount_due"],
            "amount_paid": 0,
            "amount_waived": 0,
            "amount_outstanding": od["amount_due"],
            "due_date": od["due_date"],
            "grace_end_date": od["grace_end_date"],
            "status": "Pending",
            "source_type": "Scheduled",
        })
        doc.insert(ignore_permissions=True)
        # frappe.db.set_value is intentionally used here to force the exact seed
        # amounts and status onto the obligation AFTER insert.
        #
        # Why: doc.insert() triggers validate() → _compute_status(), which would
        # override the desired seed status (e.g. "Overdue") with whatever the
        # amounts imply at insert time (e.g. "Partially Paid").  The seed data
        # intentionally represents mid-lifecycle states that cannot be created
        # via normal document flow in a single step.
        #
        # This usage is ONLY acceptable in seed/test-setup code.
        # NEVER use frappe.db.set_value to bypass validation in services, APIs,
        # or scheduler jobs that touch financial amounts.
        frappe.db.set_value("Chama Contribution Obligation", doc.name, {
            "amount_paid": od["amount_paid"],
            "amount_waived": od["amount_waived"],
            "amount_outstanding": outstanding,
            "status": od["status"],
        }, update_modified=False)
        ob_registry[key] = doc.name
        log.append(_log_created(f"Obligation {key} → {doc.name}"))
    frappe.db.commit()
    return ob_registry, log


def seed_payments(chama_registry, member_registry, payment_defs=None):
    """Returns (payment_registry, log). payment_registry = {payment_id: "CPT-000X", ...}"""
    pay_registry = {}
    log = []
    for pd in (payment_defs or PAYMENT_DEFS):
        chama_name = chama_registry[pd["chama_code"]]
        member_name = member_registry.get((pd["chama_code"], pd["phone"]))
        if not member_name:
            log.append(("SKIPPED", f"Member not found for {pd['id']}"))
            continue

        filters = {
            "chama": chama_name,
            "member": member_name,
            "amount_received": pd["amount_received"],
            "payment_date": pd["payment_date"],
        }
        if pd.get("payment_reference"):
            filters["payment_reference"] = pd["payment_reference"]

        existing = frappe.db.get_value("Chama Contribution Payment", filters, "name")
        if existing:
            pay_registry[pd["id"]] = existing
            log.append(_log_existing(f"Payment {pd['id']} → {existing}"))
            continue

        doc = frappe.get_doc({
            "doctype": "Chama Contribution Payment",
            "chama": chama_name,
            "member": member_name,
            "payment_date": pd["payment_date"],
            "amount_received": pd["amount_received"],
            "payment_method": pd["payment_method"],
            "payment_reference": pd.get("payment_reference"),
            "source_channel": pd["source_channel"],
            "status": "Recorded",
            "entered_by": "Administrator",
        })
        doc.insert(ignore_permissions=True)
        pay_registry[pd["id"]] = doc.name
        log.append(_log_created(f"Payment {pd['id']} → {doc.name}"))
    frappe.db.commit()
    return pay_registry, log


def seed_phase_b(chama_registry, member_registry):
    """
    Seed all Phase B test data idempotently.

    Returns:
        dict: manifest sub-keys b_categories, b_cycles, b_obligations, b_payments
              plus registries cat_registry, cycle_registry, ob_registry, pay_registry.
    """
    manifest = {}
    cat_registry, manifest["b_categories"] = seed_categories(chama_registry)
    cycle_registry, manifest["b_cycles"] = seed_cycles(chama_registry)
    ob_registry, manifest["b_obligations"] = seed_obligations(
        chama_registry, member_registry, cat_registry, cycle_registry
    )
    pay_registry, manifest["b_payments"] = seed_payments(chama_registry, member_registry)
    manifest["_registries"] = {
        "cat_registry": cat_registry,
        "cycle_registry": cycle_registry,
        "ob_registry": ob_registry,
        "pay_registry": pay_registry,
    }
    return manifest


def get_chama_registry():
    """
    Return the chama registry by looking up existing Chama records.
    Safe to call without seeding (raises KeyError if data is missing).
    """
    registry = {}
    for cd in CHAMA_DEFS:
        name = frappe.db.get_value("Chama", {"chama_code": cd["chama_code"]}, "name")
        if name:
            registry[cd["chama_code"]] = name
    return registry


def get_member_registry(chama_registry):
    """Return member_registry from existing DB records (no inserts)."""
    member_registry = {}
    for md in MEMBER_DEFS:
        chama_name = chama_registry.get(md["chama_code"])
        if not chama_name:
            continue
        name = frappe.db.get_value("Chama Member", {"phone": md["phone"], "chama": chama_name}, "name")
        if name:
            member_registry[(md["chama_code"], md["phone"])] = name
    return member_registry
