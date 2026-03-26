import frappe
from frappe.model.document import Document
from chama.chama_core.utils.tenant import ensure_member_matches_chama


REFERENCE_OPTIONAL_METHODS = {"Cash", "Adjustment"}


class ChamaContributionPayment(Document):
    def validate(self):
        self._validate_cross_chama()
        self._validate_amount()
        self._warn_missing_reference()
        self._check_duplicate_reference()

    def _validate_cross_chama(self):
        if self.member:
            ensure_member_matches_chama(self.member, self.chama)

    def _validate_amount(self):
        if not self.amount_received or self.amount_received <= 0:
            frappe.throw("Amount Received must be greater than zero.", frappe.ValidationError)

    def _warn_missing_reference(self):
        if self.payment_method not in REFERENCE_OPTIONAL_METHODS and not self.payment_reference:
            frappe.msgprint(
                f"Payment reference is recommended for method '{self.payment_method}'.",
                indicator="orange",
                alert=True,
            )

    def _check_duplicate_reference(self):
        """Flag payment if same chama+reference already exists (excluding self)."""
        if not self.payment_reference:
            return
        existing = frappe.db.get_value(
            "Chama Contribution Payment",
            {
                "chama": self.chama,
                "payment_reference": self.payment_reference,
                "name": ("!=", self.name or ""),
            },
            "name",
        )
        if existing:
            self.duplicate_flag = 1
            frappe.msgprint(
                f"Reference '{self.payment_reference}' matches existing payment {existing}. "
                "Duplicate flag set.",
                indicator="orange",
                alert=True,
            )
