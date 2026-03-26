"""
Phase A — Foundation: automated test suite (TDD).

Run with:
    bench --site chama.midas.com run-tests \
        --module chama.chama_core.tests.test_phase_a

Each test method is isolated (savepoint per test via IntegrationTestCase).
Seed data is committed in setUpClass and persists across tests and runs.
Test-specific records created during a test are rolled back automatically.
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from chama.chama_core.tests.seed import seed_data, get_chama_registry, get_member_registry
from chama.chama_core.services import permissions as perm_svc
from chama.chama_core.api.context import _create_audit_record


class TestPhaseAFoundation(IntegrationTestCase):
    """
    Phase A release-gate tests.

    Convention for future phases:
    - Phase B → test_phase_b.py  /  TestPhaseBContributions
    - Phase C → test_phase_c.py  /  TestPhaseCLoans
    Each uses seed.py as the shared data source.
    """

    # Disable automatic test-record generation for custom DocTypes
    doctype = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Seed is idempotent — safe to call on every test run.
        # frappe.db.commit() is called inside seed_data(), so records persist
        # beyond IntegrationTestCase's class-level rollback.
        cls.cr, cls.mr, _ = seed_data()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _set_context(self, user, active_chama=None):
        frappe.session.user = user
        frappe.session.data["active_chama"] = active_chama

    # ── A1 ────────────────────────────────────────────────────────────────────

    def test_a1_multi_chama_membership(self):
        """samuel belongs to Umoja and Harvest but NOT Jirani."""
        user = "samuel@shared.test"
        cr = self.cr

        self.assertIsNotNone(
            perm_svc.get_chama_member_for_user(user, cr["UMOJA"]),
            "samuel must have a member record in Umoja",
        )
        self.assertIsNotNone(
            perm_svc.get_chama_member_for_user(user, cr["HARVEST"]),
            "samuel must have a member record in Harvest",
        )
        self.assertIsNone(
            perm_svc.get_chama_member_for_user(user, cr["JIRANI"]),
            "samuel must NOT have a member record in Jirani",
        )

        self.assertTrue(perm_svc.user_can_access_chama(user, cr["UMOJA"]))
        self.assertTrue(perm_svc.user_can_access_chama(user, cr["HARVEST"]))
        self.assertFalse(perm_svc.user_can_access_chama(user, cr["JIRANI"]))

    # ── A2 ────────────────────────────────────────────────────────────────────

    def test_a2_same_user_different_roles_per_chama(self):
        """samuel has Treasurer in Umoja and Member in Harvest — roles are resolved independently."""
        user = "samuel@shared.test"
        cr = self.cr

        umoja_roles   = perm_svc.get_effective_chama_roles(user, cr["UMOJA"])
        harvest_roles = perm_svc.get_effective_chama_roles(user, cr["HARVEST"])

        self.assertIn("Treasurer", umoja_roles,
                      f"Expected Treasurer in Umoja roles, got: {umoja_roles}")
        self.assertIn("Member", harvest_roles,
                      f"Expected Member in Harvest roles, got: {harvest_roles}")
        self.assertNotEqual(
            set(umoja_roles), set(harvest_roles),
            "Role sets for the same user must differ across Chamas",
        )

    # ── A3 ────────────────────────────────────────────────────────────────────

    def test_a3_suspended_one_chama_active_another(self):
        """faith is Suspended in Umoja (blocked) and Active Secretary in Harvest (allowed)."""
        user = "faith@ops.test"
        cr = self.cr

        faith_umoja   = perm_svc.get_chama_member_for_user(user, cr["UMOJA"])
        faith_harvest = perm_svc.get_chama_member_for_user(user, cr["HARVEST"])

        self.assertEqual(faith_umoja.status, "Suspended")
        self.assertEqual(faith_harvest.status, "Active")

        self.assertFalse(perm_svc.user_can_access_chama(user, cr["UMOJA"]),
                         "Suspended member must not access Umoja")
        self.assertTrue(perm_svc.user_can_access_chama(user, cr["HARVEST"]),
                        "Active member must access Harvest")

        self.assertEqual(perm_svc.get_effective_chama_roles(user, cr["UMOJA"]), [],
                         "Suspended member must receive no effective roles")
        self.assertIn("Secretary", perm_svc.get_effective_chama_roles(user, cr["HARVEST"]))

    # ── A4 ────────────────────────────────────────────────────────────────────

    def test_a4_outsider_cannot_access_any_chama(self):
        """outsider@none.test has no memberships and is rejected from all Chamas."""
        user = "outsider@none.test"
        cr = self.cr

        for code in ["UMOJA", "HARVEST", "JIRANI"]:
            self.assertFalse(
                perm_svc.user_can_access_chama(user, cr[code]),
                f"outsider must be blocked from {code}",
            )

        member_count = frappe.db.count("Chama Member", {"user": user})
        self.assertEqual(member_count, 0, "outsider must have zero member records")

    # ── A5 ────────────────────────────────────────────────────────────────────

    def test_a5_dormant_member_inactive_chama(self):
        """
        joseph@jirani.test is Dormant in Jirani (Inactive Chama).
        Phase A blocks access via member.status == Dormant; Chama.status == Inactive
        is not a separate gate at this phase.
        """
        user = "joseph@jirani.test"
        cr = self.cr

        jirani_status = frappe.db.get_value("Chama", cr["JIRANI"], "status")
        self.assertEqual(jirani_status, "Inactive", "Jirani Chama must be Inactive")

        joseph = perm_svc.get_chama_member_for_user(user, cr["JIRANI"])
        self.assertIsNotNone(joseph)
        self.assertEqual(joseph.status, "Dormant")

        self.assertFalse(perm_svc.user_can_access_chama(user, cr["JIRANI"]),
                         "Dormant member must not access Jirani")
        self.assertEqual(perm_svc.get_effective_chama_roles(user, cr["JIRANI"]), [],
                         "Dormant member must receive no effective roles")

    # ── A6 ────────────────────────────────────────────────────────────────────

    def test_a6_exclusive_role_conflict_warns(self):
        """
        Assigning a second active Treasurer in Umoja triggers a warning msgprint.
        Phase A warns; it does not hard-block. The conflict record is rolled back.
        """
        cr = self.cr
        umoja = cr["UMOJA"]
        grace_name = frappe.db.get_value(
            "Chama Member", {"phone": "+254700100001", "chama": umoja}, "name"
        )

        caught = []
        original_msgprint = frappe.msgprint
        frappe.msgprint = lambda msg, title="", indicator="", **kw: caught.append(
            {"msg": str(msg), "title": str(title)}
        )
        try:
            conflict = frappe.get_doc({
                "doctype": "Chama Member Role Assignment",
                "chama": umoja,
                "member": grace_name,
                "role_name": "Treasurer",
                "effective_from": today(),
                "active": 1,
                "assigned_by": "Administrator",
            })
            conflict.insert(ignore_permissions=True)
        finally:
            frappe.msgprint = original_msgprint

        # Record was created (no hard-block) and warning fired
        self.assertTrue(
            any("Treasurer" in m["msg"] or "Treasurer" in m["title"] for m in caught),
            f"Expected exclusive-role warning for Treasurer, got: {caught}",
        )
        # Record is not committed — IntegrationTestCase savepoint will clean it up

    # ── A7 ────────────────────────────────────────────────────────────────────

    def test_a7_cross_chama_direct_access_blocked(self):
        """
        samuel in Umoja context cannot read Ann's Harvest member record.
        List filter excludes Harvest; record-level has_permission returns False.
        """
        user = "samuel@shared.test"
        cr = self.cr
        self._set_context(user, cr["UMOJA"])

        ann_name = frappe.db.get_value(
            "Chama Member", {"phone": "+254711200001", "chama": cr["HARVEST"]}, "name"
        )
        self.assertIsNotNone(ann_name, "Ann's Harvest record must exist")

        ann_doc = frappe.get_doc("Chama Member", ann_name)
        self.assertFalse(
            perm_svc.has_chama_doc_permission(ann_doc, "read", user),
            "has_chama_doc_permission must block Ann's record in Umoja context",
        )

        cond = perm_svc.get_permission_query_conditions(user)
        self.assertIn(cr["UMOJA"], cond)
        self.assertNotIn(cr["HARVEST"], cond)

    # ── A8 ────────────────────────────────────────────────────────────────────

    def test_a8_context_switch_audit_log_created(self):
        """Every context switch creates a Chama Context Session record with all required fields."""
        user = "samuel@shared.test"
        cr = self.cr

        before_count = frappe.db.count("Chama Context Session", {"user": user})

        _create_audit_record(
            user=user, active_chama=cr["HARVEST"], previous_chama=cr["UMOJA"], source_channel="WEB"
        )
        _create_audit_record(
            user=user, active_chama=cr["UMOJA"], previous_chama=cr["HARVEST"], source_channel="WEB"
        )

        after_count = frappe.db.count("Chama Context Session", {"user": user})
        self.assertEqual(after_count - before_count, 2, "Expected 2 new audit records")

        rows = frappe.db.get_all(
            "Chama Context Session",
            filters={"user": user},
            fields=["user", "active_chama", "previous_chama", "switched_at", "source_channel"],
            order_by="creation desc",
            limit=2,
        )
        for row in rows:
            self.assertEqual(row.user, user)
            self.assertTrue(row.active_chama)
            self.assertTrue(row.switched_at)
            self.assertEqual(row.source_channel, "WEB")

    # ── A9 ────────────────────────────────────────────────────────────────────

    def test_a9_in_context_records_stamp_correct_chama(self):
        """
        Records created with chama = active_chama carry the correct tenant stamp.
        Cross-chama member references are rejected by validate().
        """
        user = "grace@umoja.test"
        cr = self.cr
        self._set_context(user, cr["UMOJA"])

        grace_name = frappe.db.get_value(
            "Chama Member", {"phone": "+254700100001", "chama": cr["UMOJA"]}, "name"
        )
        role_doc = frappe.get_doc({
            "doctype": "Chama Member Role Assignment",
            "chama": cr["UMOJA"],
            "member": grace_name,
            "role_name": "Committee",
            "effective_from": today(),
            "active": 1,
            "assigned_by": "Administrator",
        })
        role_doc.insert(ignore_permissions=True)

        saved_chama = frappe.db.get_value(
            "Chama Member Role Assignment", role_doc.name, "chama"
        )
        self.assertEqual(saved_chama, cr["UMOJA"],
                         "Role assignment must be stamped with Umoja")

        # Cross-chama: samuel's Harvest member used in a Umoja role assignment → blocked
        samuel_harvest = frappe.db.get_value(
            "Chama Member", {"phone": "+254711200002", "chama": cr["HARVEST"]}, "name"
        )
        with self.assertRaises(frappe.ValidationError,
                               msg="Cross-chama member reference must raise ValidationError"):
            cross_doc = frappe.get_doc({
                "doctype": "Chama Member Role Assignment",
                "chama": cr["UMOJA"],
                "member": samuel_harvest,
                "role_name": "Committee",
                "effective_from": today(),
                "active": 1,
                "assigned_by": "Administrator",
            })
            cross_doc.insert(ignore_permissions=True)

    # ── A10 ───────────────────────────────────────────────────────────────────

    def test_a10_chama_settings_isolation(self):
        """Chama Settings are distinct per tenant; cross-context access is blocked."""
        user = "samuel@shared.test"
        cr = self.cr

        umoja_cfg   = frappe.db.get_value("Chama Settings", {"chama": cr["UMOJA"]},
                                           ["name", "budget_overrun_mode"], as_dict=True)
        harvest_cfg = frappe.db.get_value("Chama Settings", {"chama": cr["HARVEST"]},
                                           ["name", "budget_overrun_mode"], as_dict=True)
        jirani_cfg  = frappe.db.get_value("Chama Settings", {"chama": cr["JIRANI"]},
                                           ["name", "budget_overrun_mode"], as_dict=True)

        self.assertEqual(umoja_cfg.budget_overrun_mode, "Warn")
        self.assertEqual(harvest_cfg.budget_overrun_mode, "Block")
        self.assertEqual(jirani_cfg.budget_overrun_mode, "Allow With Escalation")
        self.assertNotEqual(umoja_cfg.name, harvest_cfg.name,
                            "Settings records must be distinct per Chama")

        self._set_context(user, cr["UMOJA"])

        harvest_doc = frappe.get_doc("Chama Settings", harvest_cfg.name)
        self.assertFalse(
            perm_svc.has_chama_doc_permission(harvest_doc, "read", user),
            "Harvest settings must be blocked under Umoja session",
        )

        umoja_doc = frappe.get_doc("Chama Settings", umoja_cfg.name)
        self.assertTrue(
            perm_svc.has_chama_doc_permission(umoja_doc, "read", user),
            "Umoja settings must be accessible under Umoja session",
        )
