import frappe
from frappe import _
from frappe.model.document import Document


class ChamaContextSession(Document):
    """Immutable audit log for every tenant context switch. No edit, no delete."""

    def validate(self):
        if not self.is_new():
            frappe.throw(
                _("Chama Context Session records are immutable and cannot be modified."),
                frappe.PermissionError,
            )
