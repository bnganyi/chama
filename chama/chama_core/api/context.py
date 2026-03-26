"""
Active Chama context management API.

Allows authenticated users to switch their active Chama tenant context.
Every switch is recorded in Chama Context Session for full auditability.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime

from chama.chama_core.api.responses import error_response, success_response
from chama.chama_core.services.permissions import (
    get_active_chama_for_user,
    user_can_access_chama,
)

VALID_SOURCE_CHANNELS = {"WEB", "MOBILE", "API"}


@frappe.whitelist()
def switch_active_chama(chama, source_channel="WEB"):
    """
    Switch the calling user's active Chama context.

    Validates that:
    1. The user is authenticated.
    2. The requested Chama exists.
    3. The user is an Active member of the requested Chama (or is a platform admin).

    On success the active_chama is stored in the session and an immutable
    Chama Context Session audit record is created.

    Args:
        chama (str): The Chama name to switch to.
        source_channel (str): Origin of the request — WEB | MOBILE | API.

    Returns:
        dict: Standard success or error response envelope.
    """
    user = frappe.session.user
    if not user or user == "Guest":
        return error_response(
            "UNAUTHENTICATED",
            _("You must be logged in to switch Chama context."),
            http_status_code=401,
        )

    if source_channel not in VALID_SOURCE_CHANNELS:
        source_channel = "WEB"

    if not frappe.db.exists("Chama", chama):
        return error_response(
            "NOT_FOUND",
            _("Chama {0} does not exist.").format(frappe.bold(chama)),
            http_status_code=404,
        )

    if not user_can_access_chama(user, chama):
        return error_response(
            "UNAUTHORIZED",
            _("You do not have access to Chama {0}.").format(frappe.bold(chama)),
            http_status_code=403,
        )

    previous_chama = get_active_chama_for_user(user)

    frappe.session.data["active_chama"] = chama

    _create_audit_record(
        user=user,
        active_chama=chama,
        previous_chama=previous_chama,
        source_channel=source_channel,
    )

    return success_response({"active_chama": chama, "previous_chama": previous_chama})


def get_active_chama():
    """
    Return the active Chama for the current session user.

    Returns:
        str | None: The active Chama name, or None if not set.
    """
    return frappe.session.data.get("active_chama")


def _create_audit_record(user, active_chama, previous_chama, source_channel):
    """Insert an immutable Chama Context Session record for audit purposes."""
    try:
        doc = frappe.get_doc(
            {
                "doctype": "Chama Context Session",
                "user": user,
                "active_chama": active_chama,
                "previous_chama": previous_chama or None,
                "switched_at": now_datetime(),
                "switched_by": user,
                "source_channel": source_channel,
                "session_identifier": frappe.session.sid,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        # Audit failure must never block the context switch itself.
        frappe.log_error(
            title="Chama Context Session audit insert failed",
            message=frappe.get_traceback(),
        )
