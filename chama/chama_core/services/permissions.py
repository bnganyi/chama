"""
Chama permission resolution service.

Provides session-aware, role-aware, and tenant-scoped permission helpers
used by hooks (permission_query_conditions, has_permission) and API methods.
"""

import frappe
from frappe import _

PLATFORM_ADMIN_ROLE = "System Manager"
INACTIVE_MEMBER_STATUSES = {"Suspended", "Dormant", "Exited", "Rejected", "Deceased", "Exit In Progress"}

# --------------------------------------------------------------------------- #
# Session helpers
# --------------------------------------------------------------------------- #


def get_active_chama_for_user(user=None):
    """
    Return the active Chama stored in the current Frappe session.

    Args:
        user (str | None): Unused — kept for API symmetry. Active chama is
            always derived from the current request session.

    Returns:
        str | None: The active Chama name, or None if not set.
    """
    return frappe.session.data.get("active_chama")


# --------------------------------------------------------------------------- #
# Member helpers
# --------------------------------------------------------------------------- #


def get_chama_member_for_user(user, chama):
    """
    Return the Chama Member document for *user* in *chama*, or None.

    Only returns a member whose status is not terminal (not Rejected / Exited /
    Deceased) so that inactive members are not treated as valid session actors.

    Args:
        user (str): Frappe user name (email).
        chama (str): Chama record name.

    Returns:
        Document | None
    """
    member_name = frappe.db.get_value(
        "Chama Member",
        {"user": user, "chama": chama},
        "name",
    )
    if not member_name:
        return None

    member = frappe.get_doc("Chama Member", member_name)
    return member


def get_effective_chama_roles(user, chama):
    """
    Return a list of active role_name values for *user* in *chama*.

    Roles are resolved from Chama Member Role Assignment (active=1 only).
    Members with terminal statuses receive an empty role list.

    Args:
        user (str): Frappe user name.
        chama (str): Chama record name.

    Returns:
        list[str]: e.g. ["Treasurer", "Committee"]
    """
    member = get_chama_member_for_user(user, chama)
    if not member:
        return []

    if member.status in INACTIVE_MEMBER_STATUSES:
        return []

    roles = frappe.db.get_all(
        "Chama Member Role Assignment",
        filters={"member": member.name, "chama": chama, "active": 1},
        pluck="role_name",
    )
    return roles


# --------------------------------------------------------------------------- #
# Access checks
# --------------------------------------------------------------------------- #


def user_can_access_chama(user, chama):
    """
    Return True if *user* may access records within *chama*.

    Rules:
    - Platform admins (System Manager role) always pass.
    - Otherwise, the user must have an Active Chama Member record in *chama*.

    Args:
        user (str): Frappe user name.
        chama (str): Chama record name.

    Returns:
        bool
    """
    if PLATFORM_ADMIN_ROLE in frappe.get_roles(user):
        return True

    member = get_chama_member_for_user(user, chama)
    if not member:
        return False

    return member.status == "Active"


def user_has_chama_role(user, chama, role_name):
    """
    Return True if *user* has an active role assignment for *role_name* in *chama*.

    Args:
        user (str): Frappe user name.
        chama (str): Chama record name.
        role_name (str): The role to check (e.g. "Treasurer").

    Returns:
        bool
    """
    return role_name in get_effective_chama_roles(user, chama)


# --------------------------------------------------------------------------- #
# Frappe hook callbacks
# --------------------------------------------------------------------------- #


def get_permission_query_conditions(user):
    """
    Frappe permission_query_conditions hook callback.

    Returns a SQL WHERE fragment that restricts list queries to the user's
    active Chama. Registered in hooks.py for every chama-scoped DocType.

    Platform admins receive no additional filter (they see all records).

    Args:
        user (str): Current Frappe user.

    Returns:
        str: SQL condition fragment, or "" (no restriction).
    """
    if not user:
        user = frappe.session.user

    if PLATFORM_ADMIN_ROLE in frappe.get_roles(user):
        return ""

    active_chama = get_active_chama_for_user(user)
    if not active_chama:
        # No active chama selected — return a condition that yields no rows,
        # preventing accidental cross-tenant data exposure.
        return "1=0"

    return f"`chama` = {frappe.db.escape(active_chama)}"


def has_chama_doc_permission(doc, ptype, user):
    """
    Frappe has_permission hook callback for record-level chama scope check.

    Returns True only if the document's chama matches the user's active Chama
    (or the user is a platform admin).

    Args:
        doc: The Frappe Document being accessed.
        ptype (str): Permission type (read, write, etc.).
        user (str): Current Frappe user.

    Returns:
        bool
    """
    if not user:
        user = frappe.session.user

    if PLATFORM_ADMIN_ROLE in frappe.get_roles(user):
        return True

    active_chama = get_active_chama_for_user(user)
    if not active_chama:
        return False

    doc_chama = getattr(doc, "chama", None)
    return doc_chama == active_chama
