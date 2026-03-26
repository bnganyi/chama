import frappe
from frappe.model.document import Document


class ChamaSettings(Document):
    def validate(self):
        self._validate_unique_per_chama()

    def _validate_unique_per_chama(self):
        duplicate = frappe.db.get_value(
            "Chama Settings",
            {"chama": self.chama, "name": ("!=", self.name or "")},
            "name",
        )
        if duplicate:
            frappe.throw(
                frappe._("Settings for Chama {0} already exist ({1}). Only one settings record is allowed per Chama.").format(
                    frappe.bold(self.chama), frappe.bold(duplicate)
                ),
                frappe.DuplicateEntryError,
                title=frappe._("Duplicate Chama Settings"),
            )
