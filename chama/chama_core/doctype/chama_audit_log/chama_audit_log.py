import frappe
from frappe import _
from frappe.model.document import Document


class ChamaAuditLog(Document):
    """Immutable financial audit record. Created by the system; never edited or deleted."""

    def validate(self):
        if not self.is_new():
            frappe.throw(
                _("Chama Audit Log records are immutable and cannot be modified."),
                frappe.PermissionError,
            )
