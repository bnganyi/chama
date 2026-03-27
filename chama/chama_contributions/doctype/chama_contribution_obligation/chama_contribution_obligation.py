import frappe
from frappe.model.document import Document
from chama.chama_core.utils.tenant import ensure_member_matches_chama


# Obligation Status State Machine
# ---------------------------------
# Each status is owned by exactly one actor. No actor may set a status that
# belongs to another actor without going through the prescribed transition.
#
#   Actor: DocType controller (this file — validate / _compute_status)
#       Pending → Paid          (when amount_paid + amount_waived >= amount_due on save)
#       [never sets Due, Overdue, Partially Paid, Cancelled, Waived]
#
#   Actor: Scheduler (obligation_status_jobs.py)
#       Pending → Due           (due_date reached)
#       Due → Overdue           (grace_end_date passed)
#       Partially Paid → Overdue (grace_end_date passed and still outstanding)
#       [never sets Paid, Cancelled, Waived]
#
#   Actor: Allocation Engine (allocation_engine.py — recompute_obligation_amounts_and_status)
#       * → Partially Paid      (amount_paid > 0 but not fully settled)
#       * → Paid                (amount_paid + amount_waived >= amount_due)
#       [never sets Due, Overdue, Pending]
#
#   Actor: Manual / API
#       Due → Waived            (treasurer marks obligation waived)
#       Due → Cancelled         (treasurer cancels obligation)
#
# IMPORTANT: _compute_status() intentionally does NOT set "Partially Paid".
# That responsibility belongs exclusively to the allocation engine so that
# scheduler-set "Due" and "Overdue" statuses are not silently demoted on save.
OBLIGATION_STATUS_MACHINE = {
    "controller": {
        "sets": ("Paid",),
        "never_overrides": ("Due", "Overdue", "Partially Paid", "Cancelled", "Waived"),
    },
    "scheduler": {
        "sets": ("Due", "Overdue"),
        "never_overrides": ("Paid", "Cancelled", "Waived"),
    },
    "allocation_engine": {
        "sets": ("Partially Paid", "Paid"),
        "never_overrides": ("Cancelled", "Waived"),
    },
    "manual": {
        "sets": ("Waived", "Cancelled"),
    },
}


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
        """
        Set status to Paid when fully settled. That is the only transition the
        controller is authorised to make (see OBLIGATION_STATUS_MACHINE above).

        "Partially Paid" is set exclusively by the allocation engine.
        "Due" and "Overdue" are set exclusively by the scheduler.
        This method must never override scheduler-set statuses on an obligation
        that still has an outstanding balance.
        """
        if self.status in ("Cancelled", "Waived"):
            return

        paid = flt(self.amount_paid)
        waived = flt(self.amount_waived)
        due = flt(self.amount_due)

        if paid + waived >= due:
            self.status = "Paid"


def flt(value):
    """Safe float conversion."""
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
