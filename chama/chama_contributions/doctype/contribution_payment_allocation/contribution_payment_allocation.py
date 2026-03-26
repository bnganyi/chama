import frappe
from frappe.model.document import Document


class ContributionPaymentAllocation(Document):
    def validate(self):
        if not self.allocated_amount or self.allocated_amount <= 0:
            frappe.throw("Allocated Amount must be greater than zero.", frappe.ValidationError)
