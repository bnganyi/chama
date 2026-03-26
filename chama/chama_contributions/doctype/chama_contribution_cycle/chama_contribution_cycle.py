import frappe
from frappe.model.document import Document


class ChamaContributionCycle(Document):
    def validate(self):
        self._validate_dates()
        self._validate_unique_cycle_name()

    def _validate_dates(self):
        if self.period_end < self.period_start:
            frappe.throw(
                "Period End cannot be before Period Start.",
                frappe.ValidationError,
            )

    def _validate_unique_cycle_name(self):
        existing = frappe.db.get_value(
            "Chama Contribution Cycle",
            {"chama": self.chama, "cycle_name": self.cycle_name},
            "name",
        )
        if existing and existing != self.name:
            frappe.throw(
                f"A cycle named '{self.cycle_name}' already exists in this Chama.",
                frappe.ValidationError,
            )
