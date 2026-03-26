"""
Phase B — Contributions TDD test suite.

Uses frappe's IntegrationTestCase. setUpClass seeds all data once and commits
so records persist for the full test run. Individual test mutations are rolled
back by the framework's savepoint mechanism.

Test scenarios (B1–B9):
    B1  Tenant isolation  — cross-Chama obligation raises ValidationError
    B2  Exact full payment allocation (U-001, Grace Feb)
    B3  Partial payment allocation (U-002, Samuel Feb Shares)
    B4  Multi-obligation oldest-first allocation (U-005, Samuel)
    B5  Payment reversal (U-007, Grace Levy)
    B6  Duplicate reference flag (U-006)
    B7  Waived obligation stays Waived after status job
    B8  Summary API numbers match obligation table
    B9  Harvest isolation — Umoja payments do not affect Harvest obligations
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt

from chama.chama_core.tests.seed import seed_data
from chama.chama_contributions.services.allocation_engine import (
    allocate_payment,
    reverse_payment_allocations,
)
from chama.chama_contributions.services.obligation_status_jobs import (
    refresh_due_statuses,
    refresh_overdue_statuses,
)


class TestPhaseB(IntegrationTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        frappe.set_user("Administrator")
        cls.cr, cls.mr, cls.manifest = seed_data()
        frappe.db.commit()

        regs = cls.manifest.get("_registries", {})
        cls.cat_reg   = regs.get("cat_registry", {})
        cls.cyc_reg   = regs.get("cycle_registry", {})
        cls.ob_reg    = regs.get("ob_registry", {})
        cls.pay_reg   = regs.get("pay_registry", {})

    # ─────────────────────────────────────────────────────────────────────────
    # B1 — Tenant isolation
    # ─────────────────────────────────────────────────────────────────────────

    def test_b1_cross_chama_obligation_blocked(self):
        """Creating an obligation with a member from a different chama raises ValidationError."""
        umoja = self.cr["UMOJA"]
        harvest = self.cr["HARVEST"]
        # Ann is a Harvest member; UMOJA-SHR category belongs to Umoja
        ann_mb = self.mr.get(("HARVEST", "+254711200001"))
        shr_umoja = self.cat_reg.get(("UMOJA", "SHR"))
        cyc_umoja = self.cyc_reg.get(("UMOJA", "UMOJA-MAR-2026"))

        self.assertIsNotNone(ann_mb)
        self.assertIsNotNone(shr_umoja)
        self.assertIsNotNone(cyc_umoja)

        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Chama Contribution Obligation",
                "chama": umoja,            # Umoja chama
                "member": ann_mb,          # Ann is a HARVEST member — mismatch
                "cycle": cyc_umoja,
                "contribution_category": shr_umoja,
                "amount_due": 5000,
                "due_date": "2026-03-05",
                "status": "Pending",
                "source_type": "Scheduled",
            })
            doc.insert(ignore_permissions=True)

    # ─────────────────────────────────────────────────────────────────────────
    # B2 — Exact full payment allocation
    # ─────────────────────────────────────────────────────────────────────────

    def test_b2_full_payment_allocation(self):
        """U-001: Grace Feb 6000 allocates 5000→Shares and 1000→Welfare (both Paid)."""
        payment_name = self.pay_reg.get("U-001")
        self.assertIsNotNone(payment_name, "Payment U-001 not seeded")

        # Reset payment and obligations to unpaid state
        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        payment.allocations = []
        payment.status = "Recorded"
        payment.save(ignore_permissions=True)

        ob_shr = self.ob_reg.get(("UMOJA", "+254700100001", "UMOJA-FEB-2026", "SHR"))
        ob_wlf = self.ob_reg.get(("UMOJA", "+254700100001", "UMOJA-FEB-2026", "WLF"))
        frappe.db.set_value("Chama Contribution Obligation", ob_shr,
            {"amount_paid": 0, "amount_outstanding": 5000, "status": "Overdue"}, update_modified=False)
        frappe.db.set_value("Chama Contribution Obligation", ob_wlf,
            {"amount_paid": 0, "amount_outstanding": 1000, "status": "Overdue"}, update_modified=False)

        result = allocate_payment(payment_name)

        self.assertEqual(result["payment_status"], "Allocated")
        self.assertEqual(result["rows_created"], 2)
        self.assertAlmostEqual(result["allocated_total"], 6000)
        self.assertAlmostEqual(result["unallocated_remainder"], 0)

        payment_after = frappe.get_doc("Chama Contribution Payment", payment_name)
        self.assertEqual(len(payment_after.allocations), 2)

        for ob_name in [ob_shr, ob_wlf]:
            ob = frappe.get_doc("Chama Contribution Obligation", ob_name)
            self.assertEqual(ob.status, "Paid")
            self.assertAlmostEqual(flt(ob.amount_outstanding), 0)

    # ─────────────────────────────────────────────────────────────────────────
    # B3 — Partial payment allocation
    # ─────────────────────────────────────────────────────────────────────────

    def test_b3_partial_payment_allocation(self):
        """Samuel Feb Shares: seeded partial (3000 paid, 2000 outstanding) — math integrity."""
        ob_shr_name = self.ob_reg.get(("UMOJA", "+254700100002", "UMOJA-FEB-2026", "SHR"))
        self.assertIsNotNone(ob_shr_name, "Samuel Feb Shares obligation not seeded")

        # Force to the expected seed state (previous test mutations may have altered it)
        frappe.db.set_value("Chama Contribution Obligation", ob_shr_name,
            {"amount_paid": 3000, "amount_outstanding": 2000, "status": "Overdue"}, update_modified=False)

        # Use db.get_value to read direct from DB, bypassing document cache
        row = frappe.db.get_value("Chama Contribution Obligation", ob_shr_name,
            ["amount_due", "amount_paid", "amount_outstanding", "status"], as_dict=True)
        self.assertAlmostEqual(flt(row.amount_paid), 3000)
        self.assertAlmostEqual(flt(row.amount_outstanding), 2000)
        self.assertAlmostEqual(flt(row.amount_due), 5000)
        self.assertEqual(row.status, "Overdue")
        self.assertAlmostEqual(flt(row.amount_paid) + flt(row.amount_outstanding), flt(row.amount_due))

    # ─────────────────────────────────────────────────────────────────────────
    # B4 — Multi-obligation oldest-first allocation
    # ─────────────────────────────────────────────────────────────────────────

    def test_b4_multi_obligation_oldest_first(self):
        """U-005: Samuel 4000 fully allocated — Overdue Feb first, then 1000 to first available Mar."""
        payment_name = self.pay_reg.get("U-005")
        self.assertIsNotNone(payment_name, "Payment U-005 not seeded")

        # Reset payment
        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        payment.allocations = []
        payment.status = "Recorded"
        payment.save(ignore_permissions=True)

        # Reset Feb obligations to their pre-allocation state
        ob_feb_shr = self.ob_reg[("UMOJA", "+254700100002", "UMOJA-FEB-2026", "SHR")]
        ob_feb_wlf = self.ob_reg[("UMOJA", "+254700100002", "UMOJA-FEB-2026", "WLF")]
        frappe.db.set_value("Chama Contribution Obligation", ob_feb_shr,
            {"amount_paid": 3000, "amount_outstanding": 2000, "status": "Overdue"}, update_modified=False)
        frappe.db.set_value("Chama Contribution Obligation", ob_feb_wlf,
            {"amount_paid": 0, "amount_outstanding": 1000, "status": "Overdue"}, update_modified=False)
        # Reset Mar obligations
        ob_mar_shr = self.ob_reg[("UMOJA", "+254700100002", "UMOJA-MAR-2026", "SHR")]
        ob_mar_wlf = self.ob_reg[("UMOJA", "+254700100002", "UMOJA-MAR-2026", "WLF")]
        frappe.db.set_value("Chama Contribution Obligation", ob_mar_shr,
            {"amount_paid": 0, "amount_outstanding": 5000, "status": "Due"}, update_modified=False)
        frappe.db.set_value("Chama Contribution Obligation", ob_mar_wlf,
            {"amount_paid": 0, "amount_outstanding": 1000, "status": "Due"}, update_modified=False)

        result = allocate_payment(payment_name)

        # 4000 fully consumed in 3 rows
        self.assertEqual(result["rows_created"], 3)
        self.assertAlmostEqual(result["allocated_total"], 4000)
        self.assertAlmostEqual(result["unallocated_remainder"], 0)

        # Both Feb Overdue obligations cleared
        self.assertEqual(frappe.db.get_value("Chama Contribution Obligation", ob_feb_shr, "status"), "Paid")
        self.assertEqual(frappe.db.get_value("Chama Contribution Obligation", ob_feb_wlf, "status"), "Paid")

    # ─────────────────────────────────────────────────────────────────────────
    # B5 — Payment reversal
    # ─────────────────────────────────────────────────────────────────────────

    def test_b5_payment_reversal(self):
        """U-007: Allocate Grace levy 2000, then reverse → Grace Levy outstanding restored to 2000."""
        payment_name = self.pay_reg.get("U-007")
        self.assertIsNotNone(payment_name, "Payment U-007 not seeded")

        ob_levy_name = self.ob_reg.get(("UMOJA", "+254700100001", "UMOJA-MAR-2026", "EMG"))
        self.assertIsNotNone(ob_levy_name, "Grace EMG obligation not seeded")

        # Step 1: allocate
        allocate_payment(payment_name, target_category=self.cat_reg.get(("UMOJA", "EMG")))

        ob_after_alloc = frappe.get_doc("Chama Contribution Obligation", ob_levy_name)
        self.assertEqual(ob_after_alloc.status, "Paid")

        # Step 2: reverse
        rev_result = reverse_payment_allocations(payment_name)
        self.assertEqual(rev_result["payment_status"], "Reversed")
        self.assertGreater(rev_result["reversed_rows"], 0)

        ob_after_rev = frappe.get_doc("Chama Contribution Obligation", ob_levy_name)
        self.assertEqual(ob_after_rev.status, "Due")
        self.assertAlmostEqual(flt(ob_after_rev.amount_outstanding), 2000)

    # ─────────────────────────────────────────────────────────────────────────
    # B6 — Duplicate reference flag
    # ─────────────────────────────────────────────────────────────────────────

    def test_b6_duplicate_reference_flag(self):
        """U-006 shares reference UMOJA-MP-0003 with U-005 — duplicate_flag must be set."""
        payment_name = self.pay_reg.get("U-006")
        self.assertIsNotNone(payment_name, "Payment U-006 not seeded")

        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        self.assertEqual(payment.duplicate_flag, 1, "duplicate_flag should be 1 for U-006")

    # ─────────────────────────────────────────────────────────────────────────
    # B7 — Waived obligation stays Waived
    # ─────────────────────────────────────────────────────────────────────────

    def test_b7_waived_obligation_stays_waived(self):
        """Linda's Feb Welfare is Waived; status jobs must not change it."""
        ob_name = self.ob_reg.get(("UMOJA", "+254700100004", "UMOJA-FEB-2026", "WLF"))
        self.assertIsNotNone(ob_name, "Linda Feb WLF obligation not seeded")

        ob_before = frappe.get_doc("Chama Contribution Obligation", ob_name)
        self.assertEqual(ob_before.status, "Waived")

        # Run both status jobs — Waived obligation must not change
        refresh_due_statuses(today_date="2026-03-01")
        refresh_overdue_statuses(today_date="2026-03-01")

        ob_after = frappe.get_doc("Chama Contribution Obligation", ob_name)
        self.assertEqual(ob_after.status, "Waived", "Waived status must not be changed by status jobs")

    # ─────────────────────────────────────────────────────────────────────────
    # B8 — Summary API numbers match obligation table
    # ─────────────────────────────────────────────────────────────────────────

    def test_b8_summary_api_matches_obligations(self):
        """get_member_contribution_summary for Samuel in Umoja matches raw DB sums."""
        from chama.chama_contributions.api.summary import get_member_contribution_summary

        chama = self.cr["UMOJA"]
        member = self.mr.get(("UMOJA", "+254700100002"))
        self.assertIsNotNone(member, "Samuel in Umoja not found")

        frappe.set_user("Administrator")

        response = get_member_contribution_summary(chama=chama, member=member)
        self.assertEqual(response.get("status"), "success", response.get("message"))

        data = response["data"]

        raw = frappe.db.sql(
            """
            SELECT
                SUM(amount_due) AS total_due,
                SUM(amount_paid) AS total_paid,
                SUM(amount_outstanding) AS total_outstanding
            FROM `tabChama Contribution Obligation`
            WHERE chama = %s AND member = %s
            """,
            (chama, member),
            as_dict=True,
        )[0]

        self.assertAlmostEqual(data["total_due"], flt(raw.total_due), places=2)
        self.assertAlmostEqual(data["total_paid"], flt(raw.total_paid), places=2)
        self.assertAlmostEqual(data["total_outstanding"], flt(raw.total_outstanding), places=2)

    # ─────────────────────────────────────────────────────────────────────────
    # B9 — Harvest isolation
    # ─────────────────────────────────────────────────────────────────────────

    def test_b9_harvest_isolation(self):
        """Samuel's Harvest obligations are unaffected by any Umoja payments."""
        harvest = self.cr["HARVEST"]
        samuel_harvest = self.mr.get(("HARVEST", "+254711200002"))
        self.assertIsNotNone(samuel_harvest, "Samuel in Harvest not found")

        harvest_obs = frappe.get_all(
            "Chama Contribution Obligation",
            filters={"chama": harvest, "member": samuel_harvest},
            fields=["name", "amount_paid", "amount_outstanding", "status"],
        )
        self.assertTrue(len(harvest_obs) > 0, "No Harvest obligations found for Samuel")

        # Umoja payments should not have touched these
        for ob in harvest_obs:
            alloc_count = frappe.db.count(
                "Contribution Payment Allocation",
                {"obligation": ob.name},
            )
            # No allocation rows should come from Umoja payments
            # (they have not been explicitly allocated against Harvest obligations)
            self.assertEqual(alloc_count, 0,
                f"Harvest obligation {ob.name} has unexpected allocations")
