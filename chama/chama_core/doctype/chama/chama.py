import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class Chama(Document):
    def validate(self):
        self._validate_unique_chama_name()
        self._validate_unique_chama_code()
        self._handle_archive()

    def _validate_unique_chama_name(self):
        duplicate = frappe.db.get_value(
            "Chama",
            {"chama_name": self.chama_name, "name": ("!=", self.name or "")},
            "name",
        )
        if duplicate:
            frappe.throw(
                frappe._("Chama name {0} is already in use by {1}.").format(
                    frappe.bold(self.chama_name), frappe.bold(duplicate)
                ),
                frappe.DuplicateEntryError,
                title=frappe._("Duplicate Chama Name"),
            )

    def _validate_unique_chama_code(self):
        duplicate = frappe.db.get_value(
            "Chama",
            {"chama_code": self.chama_code, "name": ("!=", self.name or "")},
            "name",
        )
        if duplicate:
            frappe.throw(
                frappe._("Chama code {0} is already in use by {1}.").format(
                    frappe.bold(self.chama_code), frappe.bold(duplicate)
                ),
                frappe.DuplicateEntryError,
                title=frappe._("Duplicate Chama Code"),
            )

    def _handle_archive(self):
        if self.status == "Archived" and not self.archived_on:
            self.archived_on = now_datetime()
        elif self.status != "Archived":
            self.archived_on = None
