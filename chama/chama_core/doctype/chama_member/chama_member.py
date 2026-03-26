import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

ACTIVE_STATUSES = {"Active"}


class ChamaMember(Document):
    def validate(self):
        self._validate_unique_national_id()
        self._validate_unique_phone()
        self._validate_join_date_required()
        self._validate_exit_date()
        self._sync_active_flag()

    def _validate_unique_national_id(self):
        duplicate = frappe.db.get_value(
            "Chama Member",
            {
                "national_id": self.national_id,
                "chama": self.chama,
                "name": ("!=", self.name or ""),
            },
            "name",
        )
        if duplicate:
            frappe.throw(
                _("National ID {0} is already registered for another member in this Chama ({1}).").format(
                    frappe.bold(self.national_id), frappe.bold(duplicate)
                ),
                frappe.DuplicateEntryError,
                title=_("Duplicate National ID"),
            )

    def _validate_unique_phone(self):
        duplicate = frappe.db.get_value(
            "Chama Member",
            {
                "phone": self.phone,
                "chama": self.chama,
                "name": ("!=", self.name or ""),
            },
            "name",
        )
        if duplicate:
            frappe.throw(
                _("Phone number {0} is already registered for another member in this Chama ({1}).").format(
                    frappe.bold(self.phone), frappe.bold(duplicate)
                ),
                frappe.DuplicateEntryError,
                title=_("Duplicate Phone Number"),
            )

    def _validate_join_date_required(self):
        if self.status == "Active" and not self.join_date:
            frappe.throw(
                _("Join Date is required when member status is Active."),
                frappe.MandatoryError,
                title=_("Join Date Missing"),
            )

    def _validate_exit_date(self):
        if self.exit_date and self.join_date:
            if getdate(self.exit_date) < getdate(self.join_date):
                frappe.throw(
                    _("Exit Date ({0}) cannot be earlier than Join Date ({1}).").format(
                        frappe.bold(self.exit_date), frappe.bold(self.join_date)
                    ),
                    frappe.ValidationError,
                    title=_("Invalid Exit Date"),
                )

    def _sync_active_flag(self):
        self.active_flag = 1 if self.status in ACTIVE_STATUSES else 0
