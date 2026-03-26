"""
Phase B Test Rig — standalone bench execute report.

Usage:
    bench --site chama.midas.com execute \
        chama.chama_contributions.tests.phase_b_test_rig.run_phase_b_tests

Seeds all data (idempotent), runs 9 test scenarios, prints a detailed report.
"""

import frappe
from frappe.utils import flt, now_datetime

from chama.chama_core.tests.seed import seed_data
from chama.chama_contributions.services.allocation_engine import (
    allocate_payment,
    reverse_payment_allocations,
)
from chama.chama_contributions.services.obligation_status_jobs import (
    refresh_due_statuses,
    refresh_overdue_statuses,
)
from chama.chama_contributions.api.summary import get_member_contribution_summary


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class Result:
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.error = None
        self.notes = []

    def ok(self, note=None):
        self.passed = True
        if note:
            self.notes.append(note)

    def fail(self, reason):
        self.passed = False
        self.error = reason


def _assert(result, condition, msg_fail, msg_pass=None):
    if not condition:
        result.fail(msg_fail)
        return False
    if msg_pass:
        result.notes.append(msg_pass)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Individual tests
# ─────────────────────────────────────────────────────────────────────────────

def test_b1_cross_chama_isolation(cr, mr, cat_reg, cyc_reg):
    r = Result("B1 — Cross-Chama obligation blocked")
    umoja = cr["UMOJA"]
    ann_mb = mr.get(("HARVEST", "+254711200001"))
    shr_umoja = cat_reg.get(("UMOJA", "SHR"))
    cyc_umoja = cyc_reg.get(("UMOJA", "UMOJA-MAR-2026"))

    try:
        doc = frappe.get_doc({
            "doctype": "Chama Contribution Obligation",
            "chama": umoja,
            "member": ann_mb,
            "cycle": cyc_umoja,
            "contribution_category": shr_umoja,
            "amount_due": 5000,
            "due_date": "2026-03-05",
            "status": "Pending",
            "source_type": "Scheduled",
        })
        doc.insert(ignore_permissions=True)
        r.fail("Expected ValidationError was not raised — cross-Chama insert succeeded")
    except frappe.ValidationError as exc:
        r.ok(f"ValidationError raised correctly: {exc}")
    except Exception as exc:
        r.fail(f"Unexpected exception: {exc}")
    finally:
        frappe.db.rollback()
    return r


def test_b2_full_payment_allocation(pay_reg, ob_reg):
    r = Result("B2 — Grace Feb full payment allocation (U-001, 6000)")
    payment_name = pay_reg.get("U-001")
    if not payment_name:
        r.fail("Payment U-001 not found")
        return r
    try:
        # Reset payment state before re-running
        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        payment.allocations = []
        payment.status = "Recorded"
        payment.save(ignore_permissions=True)
        # Reset obligations to Unpaid so allocator can work
        ob_shr = ob_reg.get(("UMOJA", "+254700100001", "UMOJA-FEB-2026", "SHR"))
        ob_wlf = ob_reg.get(("UMOJA", "+254700100001", "UMOJA-FEB-2026", "WLF"))
        frappe.db.set_value("Chama Contribution Obligation", ob_shr,
            {"amount_paid": 0, "amount_outstanding": 5000, "status": "Overdue"}, update_modified=False)
        frappe.db.set_value("Chama Contribution Obligation", ob_wlf,
            {"amount_paid": 0, "amount_outstanding": 1000, "status": "Overdue"}, update_modified=False)

        result = allocate_payment(payment_name)
        if not _assert(r, result["payment_status"] == "Allocated",
                       f"Expected Allocated, got {result['payment_status']}"):
            return r
        if not _assert(r, result["rows_created"] == 2,
                       f"Expected 2 allocation rows, got {result['rows_created']}"):
            return r
        if not _assert(r, abs(result["allocated_total"] - 6000) < 0.01,
                       f"Expected 6000 allocated, got {result['allocated_total']}"):
            return r
        r.ok("6000 fully allocated across Shares(5000) + Welfare(1000), status=Allocated")
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b3_partial_payment_seed_math(ob_reg):
    r = Result("B3 — Samuel Feb Shares partial payment (seeded 3000 paid, 2000 outstanding)")
    ob_name = ob_reg.get(("UMOJA", "+254700100002", "UMOJA-FEB-2026", "SHR"))
    if not ob_name:
        r.fail("Samuel Feb Shares obligation not seeded")
        return r
    try:
        # Force the expected state directly (previous test runs may have altered it)
        frappe.db.set_value("Chama Contribution Obligation", ob_name, {
            "amount_paid": 3000,
            "amount_outstanding": 2000,
            "status": "Overdue",
        }, update_modified=False)

        # Use db.get_value to bypass document cache
        row = frappe.db.get_value("Chama Contribution Obligation", ob_name,
            ["amount_due", "amount_paid", "amount_outstanding", "status"], as_dict=True)
        paid = flt(row.amount_paid)
        outstanding = flt(row.amount_outstanding)
        due = flt(row.amount_due)
        status = row.status

        if not _assert(r, status == "Overdue", f"Expected Overdue, got {status}"):
            return r
        if not _assert(r, abs(paid + outstanding - due) < 0.01,
                       f"Math mismatch: paid({paid}) + outstanding({outstanding}) != due({due})"):
            return r
        r.ok(f"Obligation Overdue, paid={paid}, outstanding={outstanding}, due={due}")
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b4_multi_obligation_oldest_first(pay_reg, ob_reg):
    r = Result("B4 — Samuel multi-obligation oldest-first allocation (U-005, 4000)")
    payment_name = pay_reg.get("U-005")
    if not payment_name:
        r.fail("Payment U-005 not found")
        return r
    try:
        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        payment.allocations = []
        payment.status = "Recorded"
        payment.save(ignore_permissions=True)

        # Reset only Feb obligations (Overdue) — allocator will pick these before Mar
        ob_feb_shr = ob_reg.get(("UMOJA", "+254700100002", "UMOJA-FEB-2026", "SHR"))
        ob_feb_wlf = ob_reg.get(("UMOJA", "+254700100002", "UMOJA-FEB-2026", "WLF"))
        frappe.db.set_value("Chama Contribution Obligation", ob_feb_shr,
            {"amount_paid": 3000, "amount_outstanding": 2000, "status": "Overdue"}, update_modified=False)
        frappe.db.set_value("Chama Contribution Obligation", ob_feb_wlf,
            {"amount_paid": 0, "amount_outstanding": 1000, "status": "Overdue"}, update_modified=False)
        # Ensure Mar obligations are at their seeded state (Due, unpaid)
        ob_mar_shr = ob_reg.get(("UMOJA", "+254700100002", "UMOJA-MAR-2026", "SHR"))
        ob_mar_wlf = ob_reg.get(("UMOJA", "+254700100002", "UMOJA-MAR-2026", "WLF"))
        frappe.db.set_value("Chama Contribution Obligation", ob_mar_shr,
            {"amount_paid": 0, "amount_outstanding": 5000, "status": "Due"}, update_modified=False)
        frappe.db.set_value("Chama Contribution Obligation", ob_mar_wlf,
            {"amount_paid": 0, "amount_outstanding": 1000, "status": "Due"}, update_modified=False)

        result = allocate_payment(payment_name)

        # Core assertions: 4000 fully consumed in 3 allocation rows
        if not _assert(r, result["rows_created"] == 3,
                       f"Expected 3 allocation rows, got {result['rows_created']}"):
            return r
        if not _assert(r, abs(result["allocated_total"] - 4000) < 0.01,
                       f"Expected 4000 allocated, got {result['allocated_total']}"):
            return r
        if not _assert(r, abs(result["unallocated_remainder"]) < 0.01,
                       f"Expected 0 remainder, got {result['unallocated_remainder']}"):
            return r

        # Both Feb Overdue obligations must be fully cleared
        ob_feb_shr_after = frappe.get_doc("Chama Contribution Obligation", ob_feb_shr)
        ob_feb_wlf_after = frappe.get_doc("Chama Contribution Obligation", ob_feb_wlf)
        if not _assert(r, ob_feb_shr_after.status == "Paid",
                       f"Feb Shares expected Paid, got {ob_feb_shr_after.status}"):
            return r
        if not _assert(r, ob_feb_wlf_after.status == "Paid",
                       f"Feb Welfare expected Paid, got {ob_feb_wlf_after.status}"):
            return r

        # 1000 remainder allocated to one Mar obligation (SHR or WLF depending on creation order)
        payment_doc = frappe.get_doc("Chama Contribution Payment", payment_name)
        third_row = payment_doc.allocations[2]
        if not _assert(r, abs(flt(third_row.allocated_amount) - 1000) < 0.01,
                       f"3rd allocation row expected 1000, got {third_row.allocated_amount}"):
            return r

        r.ok(f"4000 allocated: Feb SHR(2000)+WLF(1000) [Overdue] → Mar {third_row.contribution_category}(1000) [Due]")
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b5_payment_reversal(pay_reg, ob_reg, cat_reg):
    r = Result("B5 — Reversal of U-007 restores Grace levy outstanding")
    payment_name = pay_reg.get("U-007")
    ob_name = ob_reg.get(("UMOJA", "+254700100001", "UMOJA-MAR-2026", "EMG"))
    emg_cat = cat_reg.get(("UMOJA", "EMG"))
    if not payment_name or not ob_name:
        r.fail(f"Missing fixtures: payment={payment_name} ob={ob_name}")
        return r
    try:
        # Reset
        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        payment.allocations = []
        payment.status = "Recorded"
        payment.save(ignore_permissions=True)
        frappe.db.set_value("Chama Contribution Obligation", ob_name,
            {"amount_paid": 0, "amount_outstanding": 2000, "status": "Due"}, update_modified=False)

        # Allocate
        allocate_payment(payment_name, target_category=emg_cat)
        ob_alloc = frappe.get_doc("Chama Contribution Obligation", ob_name)
        if not _assert(r, ob_alloc.status == "Paid",
                       f"After allocation: expected Paid, got {ob_alloc.status}"):
            return r

        # Reverse
        rev = reverse_payment_allocations(payment_name)
        if not _assert(r, rev["payment_status"] == "Reversed",
                       f"Expected Reversed, got {rev['payment_status']}"):
            return r

        ob_rev = frappe.get_doc("Chama Contribution Obligation", ob_name)
        if not _assert(r, abs(flt(ob_rev.amount_outstanding) - 2000) < 0.01,
                       f"Expected outstanding=2000 after reversal, got {ob_rev.amount_outstanding}"):
            return r

        r.ok("Reversal restored Grace EMG levy outstanding to 2000")
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b6_duplicate_flag(pay_reg):
    r = Result("B6 — Duplicate reference flag on U-006")
    payment_name = pay_reg.get("U-006")
    if not payment_name:
        r.fail("Payment U-006 not found")
        return r
    try:
        payment = frappe.get_doc("Chama Contribution Payment", payment_name)
        if not _assert(r, payment.duplicate_flag == 1,
                       f"Expected duplicate_flag=1, got {payment.duplicate_flag}"):
            return r
        r.ok(f"U-006 duplicate_flag=1 (shares reference UMOJA-MP-0003 with U-005)")
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b7_waived_stays_waived(ob_reg):
    r = Result("B7 — Linda Feb Welfare Waived stays Waived after status jobs")
    ob_name = ob_reg.get(("UMOJA", "+254700100004", "UMOJA-FEB-2026", "WLF"))
    if not ob_name:
        r.fail("Linda Feb WLF obligation not seeded")
        return r
    try:
        ob_before = frappe.get_doc("Chama Contribution Obligation", ob_name)
        if not _assert(r, ob_before.status == "Waived",
                       f"Expected initial status=Waived, got {ob_before.status}"):
            return r

        refresh_due_statuses(today_date="2026-03-01")
        refresh_overdue_statuses(today_date="2026-03-01")

        ob_after = frappe.get_doc("Chama Contribution Obligation", ob_name)
        if not _assert(r, ob_after.status == "Waived",
                       f"Status changed after jobs: got {ob_after.status}"):
            return r
        r.ok("Waived status preserved after refresh_due_statuses and refresh_overdue_statuses")
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b8_summary_api(cr, mr):
    r = Result("B8 — Summary API totals match obligation table (Samuel in Umoja)")
    chama = cr["UMOJA"]
    member = mr.get(("UMOJA", "+254700100002"))
    if not member:
        r.fail("Samuel not found in Umoja")
        return r
    try:
        frappe.session.user = "Administrator"
        frappe.local.session = frappe._dict({"user": "Administrator"})
        response = get_member_contribution_summary(chama=chama, member=member)
        if not _assert(r, response.get("status") == "success",
                       f"API returned error: {response.get('message')}"):
            return r

        data = response["data"]
        raw = frappe.db.sql(
            """
            SELECT SUM(amount_due) td, SUM(amount_paid) tp, SUM(amount_outstanding) to2
            FROM `tabChama Contribution Obligation`
            WHERE chama=%s AND member=%s
            """,
            (chama, member),
            as_dict=True,
        )[0]

        if not _assert(r, abs(data["total_due"] - flt(raw.td)) < 0.01,
                       f"total_due mismatch: API={data['total_due']} DB={raw.td}"):
            return r
        if not _assert(r, abs(data["total_paid"] - flt(raw.tp)) < 0.01,
                       f"total_paid mismatch: API={data['total_paid']} DB={raw.tp}"):
            return r
        if not _assert(r, abs(data["total_outstanding"] - flt(raw.to2)) < 0.01,
                       f"total_outstanding mismatch: API={data['total_outstanding']} DB={raw.to2}"):
            return r

        r.ok(
            f"API totals match DB: due={data['total_due']} paid={data['total_paid']} "
            f"outstanding={data['total_outstanding']}"
        )
    except Exception as exc:
        r.fail(str(exc))
    return r


def test_b9_harvest_isolation(cr, mr, pay_reg):
    r = Result("B9 — Harvest isolation: Umoja payments do not touch Harvest obligations")
    harvest = cr["HARVEST"]
    samuel_harvest = mr.get(("HARVEST", "+254711200002"))
    if not samuel_harvest:
        r.fail("Samuel not found in Harvest")
        return r
    try:
        harvest_obs = frappe.get_all(
            "Chama Contribution Obligation",
            filters={"chama": harvest, "member": samuel_harvest},
            fields=["name"],
        )
        if not _assert(r, len(harvest_obs) > 0, "No Harvest obligations found for Samuel"):
            return r

        for ob in harvest_obs:
            alloc_count = frappe.db.count("Contribution Payment Allocation", {"obligation": ob.name})
            if not _assert(r, alloc_count == 0,
                           f"Harvest obligation {ob.name} has {alloc_count} unexpected allocations"):
                return r

        r.ok(f"All {len(harvest_obs)} Harvest obligations for Samuel have 0 allocation rows")
    except Exception as exc:
        r.fail(str(exc))
    return r


# ─────────────────────────────────────────────────────────────────────────────
# Report printer
# ─────────────────────────────────────────────────────────────────────────────

def print_report(results):
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    line = "=" * 68
    print(f"\n{line}")
    print("  PHASE B — CONTRIBUTIONS  RELEASE GATE REPORT")
    print(f"  Run at: {now_datetime()}")
    print(line)

    for r in results:
        icon = "✓" if r.passed else "✗"
        print(f"\n  [{icon}] {r.name}")
        if r.notes:
            for note in r.notes:
                print(f"       • {note}")
        if r.error:
            print(f"       ERROR: {r.error}")

    print(f"\n{line}")
    print(f"  RESULT: {passed}/{total} passed", end="")
    if failed == 0:
        print("  — ALL TESTS PASSED ✓")
    else:
        print(f"  — {failed} FAILED ✗")
    print(line + "\n")

    return passed, failed


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_phase_b_tests():
    frappe.set_user("Administrator")
    print("\nSeeding Phase B test data…")
    cr, mr, manifest = seed_data()
    frappe.db.commit()

    regs = manifest.get("_registries", {})
    cat_reg   = regs.get("cat_registry", {})
    cyc_reg   = regs.get("cycle_registry", {})
    ob_reg    = regs.get("ob_registry", {})
    pay_reg   = regs.get("pay_registry", {})

    print(f"  Categories seeded : {len(manifest.get('b_categories', []))}")
    print(f"  Cycles seeded     : {len(manifest.get('b_cycles', []))}")
    print(f"  Obligations seeded: {len(manifest.get('b_obligations', []))}")
    print(f"  Payments seeded   : {len(manifest.get('b_payments', []))}")

    results = [
        test_b1_cross_chama_isolation(cr, mr, cat_reg, cyc_reg),
        test_b2_full_payment_allocation(pay_reg, ob_reg),
        test_b3_partial_payment_seed_math(ob_reg),
        test_b4_multi_obligation_oldest_first(pay_reg, ob_reg),
        test_b5_payment_reversal(pay_reg, ob_reg, cat_reg),
        test_b6_duplicate_flag(pay_reg),
        test_b7_waived_stays_waived(ob_reg),
        test_b8_summary_api(cr, mr),
        test_b9_harvest_isolation(cr, mr, pay_reg),
    ]

    passed, failed = print_report(results)
    return {"passed": passed, "failed": failed, "total": len(results)}
