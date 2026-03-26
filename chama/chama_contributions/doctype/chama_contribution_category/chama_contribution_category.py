import frappe
from frappe.model.document import Document


class ChamaContributionCategory(Document):
    def validate(self):
        self._validate_unique_category_name()
        self._validate_unique_category_code()
        self._validate_fixed_amount()
        self._validate_dates()

    def _validate_unique_category_name(self):
        existing = frappe.db.get_value(
            "Chama Contribution Category",
            {"chama": self.chama, "category_name": self.category_name},
            "name",
        )
        if existing and existing != self.name:
            frappe.throw(
                f"A contribution category named '{self.category_name}' already exists in this Chama.",
                frappe.ValidationError,
            )

    def _validate_unique_category_code(self):
        existing = frappe.db.get_value(
            "Chama Contribution Category",
            {"chama": self.chama, "category_code": self.category_code},
            "name",
        )
        if existing and existing != self.name:
            frappe.throw(
                f"Category code '{self.category_code}' is already used in this Chama.",
                frappe.ValidationError,
            )

    def _validate_fixed_amount(self):
        if self.amount_type == "Fixed" and (not self.default_amount or self.default_amount <= 0):
            frappe.throw(
                "Default Amount must be greater than zero for Fixed amount categories.",
                frappe.ValidationError,
            )

    def _validate_dates(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw(
                "End Date cannot be before Start Date.",
                frappe.ValidationError,
            )
