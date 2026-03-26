import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

EXCLUSIVE_ROLES = {"Treasurer", "Chair", "Secretary"}


class ChamaMemberRoleAssignment(Document):
    def validate(self):
        self._validate_member_chama_consistency()
        self._validate_date_range()
        self._auto_deactivate_if_expired()
        self._warn_exclusive_role_overlap()

    def _validate_member_chama_consistency(self):
        member_chama = frappe.db.get_value("Chama Member", self.member, "chama")
        if member_chama != self.chama:
            frappe.throw(
                _("Member {0} belongs to Chama {1}, not {2}. A role assignment must reference a member from the same Chama.").format(
                    frappe.bold(self.member),
                    frappe.bold(member_chama),
                    frappe.bold(self.chama),
                ),
                frappe.ValidationError,
                title=_("Cross-Chama Member Reference"),
            )

    def _validate_date_range(self):
        if self.effective_to and self.effective_from:
            if getdate(self.effective_to) < getdate(self.effective_from):
                frappe.throw(
                    _("Effective To ({0}) must be on or after Effective From ({1}).").format(
                        frappe.bold(self.effective_to), frappe.bold(self.effective_from)
                    ),
                    frappe.ValidationError,
                    title=_("Invalid Date Range"),
                )

    def _auto_deactivate_if_expired(self):
        if self.effective_to and getdate(self.effective_to) < getdate(today()):
            self.active = 0

    def _warn_exclusive_role_overlap(self):
        if self.role_name not in EXCLUSIVE_ROLES:
            return

        overlap = frappe.db.get_value(
            "Chama Member Role Assignment",
            {
                "chama": self.chama,
                "role_name": self.role_name,
                "active": 1,
                "name": ("!=", self.name or ""),
            },
            "name",
        )
        if overlap:
            frappe.msgprint(
                _("Warning: An active {0} assignment already exists ({1}) in this Chama. Please review before saving.").format(
                    frappe.bold(self.role_name), frappe.bold(overlap)
                ),
                title=_("Duplicate Executive Role"),
                indicator="orange",
            )
