"""
Tenant validation utilities for Chama isolation enforcement.

All functions raise frappe.ValidationError on mismatch.
Supports both Document objects and dict-like inputs.
"""

import frappe
from frappe import _


def _get_chama_value(obj):
    """Extract chama value from a Document, dict, or string."""
    if isinstance(obj, str):
        return obj
    if hasattr(obj, "chama"):
        return obj.chama
    if isinstance(obj, dict):
        return obj.get("chama")
    frappe.throw(
        _("Cannot extract chama value from object of type {0}.").format(type(obj).__name__),
        frappe.ValidationError,
    )


def ensure_same_chama(*docs_or_dicts):
    """
    Raise ValidationError if not all records share the same chama value.

    Accepts any mix of Document objects, dicts, or plain chama name strings.
    Requires at least two arguments.
    """
    if len(docs_or_dicts) < 2:
        frappe.throw(
            _("ensure_same_chama requires at least two arguments."),
            frappe.ValidationError,
        )

    values = [_get_chama_value(obj) for obj in docs_or_dicts]
    unique_values = set(filter(None, values))

    if len(unique_values) > 1:
        frappe.throw(
            _("Cross-Chama operation detected. All records must belong to the same Chama. Found: {0}").format(
                ", ".join(sorted(unique_values))
            ),
            frappe.ValidationError,
            title=_("Chama Isolation Violation"),
        )

    if not unique_values:
        frappe.throw(
            _("No chama value found on the provided records. Each record must have a chama field."),
            frappe.ValidationError,
            title=_("Missing Chama Reference"),
        )


def ensure_doc_matches_chama(doc, chama_name):
    """
    Raise ValidationError if doc.chama does not equal chama_name.

    Args:
        doc: A Document object or dict with a chama field.
        chama_name (str): The expected Chama name.
    """
    doc_chama = _get_chama_value(doc)
    if doc_chama != chama_name:
        doc_id = getattr(doc, "name", None) or (doc.get("name") if isinstance(doc, dict) else str(doc))
        frappe.throw(
            _("Record {0} belongs to Chama {1} but the expected Chama is {2}.").format(
                frappe.bold(doc_id),
                frappe.bold(doc_chama),
                frappe.bold(chama_name),
            ),
            frappe.ValidationError,
            title=_("Chama Mismatch"),
        )


def ensure_member_matches_chama(member_name, chama_name):
    """
    Fetch Chama Member and confirm it belongs to chama_name.

    Args:
        member_name (str): The name (ID) of the Chama Member record.
        chama_name (str): The expected Chama name.

    Raises:
        frappe.ValidationError if the member belongs to a different Chama.
        frappe.DoesNotExistError if the member record is not found.
    """
    member_chama = frappe.db.get_value("Chama Member", member_name, "chama")
    if not member_chama:
        frappe.throw(
            _("Chama Member {0} does not exist.").format(frappe.bold(member_name)),
            frappe.DoesNotExistError,
        )
    if member_chama != chama_name:
        frappe.throw(
            _("Chama Member {0} belongs to Chama {1} but the expected Chama is {2}.").format(
                frappe.bold(member_name),
                frappe.bold(member_chama),
                frappe.bold(chama_name),
            ),
            frappe.ValidationError,
            title=_("Member-Chama Mismatch"),
        )


def get_member_for_user_in_chama(user, chama_name):
    """
    Return the Chama Member name (record ID) for this user in the given Chama.

    Args:
        user (str): Frappe user name (email).
        chama_name (str): The Chama to look up.

    Returns:
        str | None: The Chama Member record name, or None if not found.
    """
    return frappe.db.get_value(
        "Chama Member",
        {"user": user, "chama": chama_name},
        "name",
    )
