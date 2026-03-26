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
    Seed all Phase A test data idempotently.

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
    return cr, mr, manifest


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
