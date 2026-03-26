import frappe
from frappe.model.document import Document
from chama.chama_core.utils.tenant import ensure_member_matches_chama


class ChamaContributionObligation(Document):
    def validate(self):
        self._validate_cross_chama()
        self._validate_amount_due()
        self._compute_outstanding()
        self._compute_status()

    def _validate_cross_chama(self):
        """Ensure member and category both belong to this obligation's chama."""
        if self.member:
            ensure_member_matches_chama(self.member, self.chama)
        if self.contribution_category:
            cat_chama = frappe.db.get_value(
                "Chama Contribution Category", self.contribution_category, "chama"
            )
            if cat_chama and cat_chama != self.chama:
                frappe.throw(
                    f"Contribution Category {self.contribution_category} belongs to a different Chama.",
                    frappe.ValidationError,
                )
        if self.cycle:
            cycle_chama = frappe.db.get_value(
                "Chama Contribution Cycle", self.cycle, "chama"
            )
            if cycle_chama and cycle_chama != self.chama:
                frappe.throw(
                    f"Cycle {self.cycle} belongs to a different Chama.",
                    frappe.ValidationError,
                )

    def _validate_amount_due(self):
        if not self.amount_due or self.amount_due <= 0:
            frappe.throw("Amount Due must be greater than zero.", frappe.ValidationError)

    def _compute_outstanding(self):
        paid = flt(self.amount_paid)
        waived = flt(self.amount_waived)
        outstanding = flt(self.amount_due) - paid - waived
        self.amount_outstanding = max(outstanding, 0)

    def _compute_status(self):
        """Derive status from amounts. Terminal statuses are never overridden here."""
        if self.status in ("Cancelled", "Waived"):
            return

        paid = flt(self.amount_paid)
        waived = flt(self.amount_waived)
        due = flt(self.amount_due)

        if paid + waived >= due:
            self.status = "Paid"
        elif paid > 0:
            self.status = "Partially Paid"


def flt(value):
    """Safe float conversion."""
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
