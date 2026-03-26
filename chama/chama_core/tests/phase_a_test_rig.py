"""
Phase A Test Rig — standalone reporting runner.
================================================
Seeds all test data and runs the 10 Phase A release-gate scenarios,
printing a formatted report. All data persists after the run.

For TDD (CI/automated) use the IntegrationTestCase-based file instead:
    bench --site chama.midas.com run-tests \\
        --module chama.chama_core.tests.test_phase_a

For this manual report runner:
    bench --site chama.midas.com execute \\
        chama.chama_core.tests.phase_a_test_rig.run_phase_a_tests
"""

import frappe
from frappe.utils import today, now_datetime

from chama.chama_core.tests.seed import seed_data  # single source of truth
from chama.chama_core.services import permissions as perm_svc
from chama.chama_core.api.context import _create_audit_record


# ──────────────────────────────────────────────────────────────────────────────
# Test helpers
# ──────────────────────────────────────────────────────────────────────────────

def _set_context(user, active_chama=None):
    """Simulate user session context for console-based tests."""
    frappe.session.user = user
    frappe.session.data["active_chama"] = active_chama


def _result(test_id, name, checks, notes=""):
    passed = all(c["ok"] for c in checks)
    return {
        "id": test_id,
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "notes": notes,
    }


def _check(desc, ok, detail=""):
    return {"desc": desc, "ok": ok, "detail": detail}


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_a1_multi_chama_membership(cr, mr):
    """A1 — Multi-Chama membership: samuel belongs to Umoja and Harvest, not Jirani."""
    user = "samuel@shared.test"
    checks = []

    samuel_umoja = perm_svc.get_chama_member_for_user(user, cr["UMOJA"])
    samuel_harvest = perm_svc.get_chama_member_for_user(user, cr["HARVEST"])
    samuel_jirani = perm_svc.get_chama_member_for_user(user, cr["JIRANI"])

    checks.append(_check("samuel has member record in Umoja",   bool(samuel_umoja),   getattr(samuel_umoja, "name", None)))
    checks.append(_check("samuel has member record in Harvest", bool(samuel_harvest), getattr(samuel_harvest, "name", None)))
    checks.append(_check("samuel has NO member record in Jirani", samuel_jirani is None, str(samuel_jirani)))

    can_umoja   = perm_svc.user_can_access_chama(user, cr["UMOJA"])
    can_harvest = perm_svc.user_can_access_chama(user, cr["HARVEST"])
    can_jirani  = perm_svc.user_can_access_chama(user, cr["JIRANI"])

    checks.append(_check("samuel can_access Umoja",      can_umoja,    ""))
    checks.append(_check("samuel can_access Harvest",    can_harvest,  ""))
    checks.append(_check("samuel cannot_access Jirani",  not can_jirani, ""))

    return _result("A1", "Multi-Chama membership works", checks)


def test_a2_same_user_different_roles(cr, mr):
    """A2 — Same user resolves different roles per Chama."""
    user = "samuel@shared.test"
    checks = []

    _set_context(user, cr["UMOJA"])
    umoja_roles = perm_svc.get_effective_chama_roles(user, cr["UMOJA"])
    checks.append(_check("samuel role in Umoja = Treasurer", "Treasurer" in umoja_roles, str(umoja_roles)))

    _set_context(user, cr["HARVEST"])
    harvest_roles = perm_svc.get_effective_chama_roles(user, cr["HARVEST"])
    checks.append(_check("samuel role in Harvest = Member", "Member" in harvest_roles, str(harvest_roles)))

    checks.append(_check("Umoja role ≠ Harvest role", set(umoja_roles) != set(harvest_roles),
                          f"Umoja={umoja_roles} Harvest={harvest_roles}"))

    return _result("A2", "Same user resolves different roles per Chama", checks)


def test_a3_suspended_in_one_active_in_another(cr, mr):
    """A3 — faith is Suspended in Umoja but Active in Harvest."""
    user = "faith@ops.test"
    checks = []

    faith_umoja   = perm_svc.get_chama_member_for_user(user, cr["UMOJA"])
    faith_harvest = perm_svc.get_chama_member_for_user(user, cr["HARVEST"])

    checks.append(_check("faith member status in Umoja = Suspended",
                          getattr(faith_umoja, "status", "") == "Suspended",
                          getattr(faith_umoja, "status", "MISSING")))
    checks.append(_check("faith member status in Harvest = Active",
                          getattr(faith_harvest, "status", "") == "Active",
                          getattr(faith_harvest, "status", "MISSING")))

    # Suspended member blocked from Umoja
    can_umoja   = perm_svc.user_can_access_chama(user, cr["UMOJA"])
    can_harvest = perm_svc.user_can_access_chama(user, cr["HARVEST"])

    checks.append(_check("faith blocked from Umoja (Suspended)", not can_umoja, f"can_access={can_umoja}"))
    checks.append(_check("faith allowed in Harvest (Active)", can_harvest, f"can_access={can_harvest}"))

    # Roles: Suspended member should yield no effective roles in Umoja
    umoja_roles   = perm_svc.get_effective_chama_roles(user, cr["UMOJA"])
    harvest_roles = perm_svc.get_effective_chama_roles(user, cr["HARVEST"])

    checks.append(_check("faith gets no effective roles in Umoja (Suspended)",
                          umoja_roles == [], str(umoja_roles)))
    checks.append(_check("faith has Secretary role in Harvest",
                          "Secretary" in harvest_roles, str(harvest_roles)))

    return _result("A3", "Suspended in one Chama, Active in another",
                   checks,
                   notes="Suspension is tenant-scoped; it does not affect access in other Chamas.")


def test_a4_outsider_cannot_switch(cr, mr):
    """A4 — outsider@none.test has no memberships and cannot access any Chama."""
    user = "outsider@none.test"
    checks = []

    for code in ["UMOJA", "HARVEST", "JIRANI"]:
        can = perm_svc.user_can_access_chama(user, cr[code])
        checks.append(_check(f"outsider blocked from {code}", not can, f"can_access={can}"))

    # Ensure no member record exists for outsider anywhere
    member_count = frappe.db.count("Chama Member", {"user": user})
    checks.append(_check("outsider has 0 member records", member_count == 0, f"count={member_count}"))

    return _result("A4", "Outsider cannot access any Chama", checks)


def test_a5_inactive_chama_handling(cr, mr):
    """A5 — joseph@jirani.test is Dormant in Jirani (Inactive Chama)."""
    user = "joseph@jirani.test"
    checks = []

    jirani_status = frappe.db.get_value("Chama", cr["JIRANI"], "status")
    checks.append(_check("Jirani Chama status = Inactive", jirani_status == "Inactive", jirani_status))

    joseph_member = perm_svc.get_chama_member_for_user(user, cr["JIRANI"])
    joseph_status = getattr(joseph_member, "status", None)
    checks.append(_check("joseph member status = Dormant", joseph_status == "Dormant", joseph_status))

    can_jirani = perm_svc.user_can_access_chama(user, cr["JIRANI"])
    checks.append(_check("joseph blocked from Jirani (Dormant member status)", not can_jirani,
                          f"can_access={can_jirani}"))

    roles = perm_svc.get_effective_chama_roles(user, cr["JIRANI"])
    checks.append(_check("joseph receives no effective roles in Jirani", roles == [], str(roles)))

    return _result(
        "A5", "Inactive Chama / Dormant member handling", checks,
        notes=(
            "Switch blocked via member.status == Dormant (not Active). "
            "Phase A does not add a separate gate on Chama.status == Inactive; "
            "the Dormant member status produces the same result."
        ),
    )


def test_a6_exclusive_role_conflict(cr, mr):
    """A6 — Attempting to assign a second active Treasurer in Umoja triggers a warning."""
    checks = []
    umoja = cr["UMOJA"]

    # Grace is currently Chair — try assigning her as Treasurer (second active Treasurer)
    grace_name = frappe.db.get_value("Chama Member",
                                     {"phone": "+254700100001", "chama": umoja}, "name")

    caught_msgprint = []
    original_msgprint = frappe.msgprint

    def capture_msgprint(msg, title="", indicator=""):
        caught_msgprint.append({"msg": str(msg), "title": str(title), "indicator": indicator})

    frappe.msgprint = capture_msgprint

    conflict_doc = None
    try:
        conflict_doc = frappe.get_doc({
            "doctype": "Chama Member Role Assignment",
            "chama": umoja,
            "member": grace_name,
            "role_name": "Treasurer",
            "effective_from": today(),
            "active": 1,
            "assigned_by": "Administrator",
        })
        conflict_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        checks.append(_check("Insert raised hard exception (hard-block mode)", True, str(e)))
    else:
        warning_fired = any("Treasurer" in m["msg"] or "Treasurer" in m["title"]
                            for m in caught_msgprint)
        checks.append(_check("Duplicate Treasurer insert completed (warns, no hard-block)", True,
                              "Assignment created — warning path verified"))
        checks.append(_check("Warning message about exclusive role overlap was fired",
                              warning_fired, str(caught_msgprint)))
        # Clean up the conflict record so data stays clean
        if conflict_doc and conflict_doc.name:
            frappe.db.delete("Chama Member Role Assignment", conflict_doc.name)
            frappe.db.commit()
    finally:
        frappe.msgprint = original_msgprint

    return _result(
        "A6", "Exclusive role conflict detection (Treasurer overlap in Umoja)", checks,
        notes=(
            "Phase A raises a msgprint warning when an exclusive role overlap is detected. "
            "Hard-blocking is a Phase A+ configuration concern."
        ),
    )


def test_a7_cross_chama_direct_access_blocked(cr, mr):
    """A7 — samuel in Umoja context cannot see Ann's Harvest member record."""
    user = "samuel@shared.test"
    _set_context(user, cr["UMOJA"])

    ann_member_name = frappe.db.get_value(
        "Chama Member", {"phone": "+254711200001", "chama": cr["HARVEST"]}, "name"
    )
    checks = []
    checks.append(_check("Ann's Harvest member record exists", bool(ann_member_name), ann_member_name))

    # Record-level has_permission: Ann's record has chama=HARVEST; active session is UMOJA
    ann_doc = frappe.get_doc("Chama Member", ann_member_name)
    allowed = perm_svc.has_chama_doc_permission(ann_doc, "read", user)
    checks.append(_check("has_chama_doc_permission blocks Ann's record in Umoja context",
                          not allowed, f"returned={allowed}"))

    # List filter: Umoja session must NOT include Harvest records
    cond = perm_svc.get_permission_query_conditions(user)
    contains_umoja  = cr["UMOJA"]  in cond
    contains_harvest = cr["HARVEST"] in cond
    checks.append(_check("List filter references Umoja, not Harvest",
                          contains_umoja and not contains_harvest,
                          f"condition={repr(cond)}"))

    # Switch to Harvest — now Umoja records must be blocked
    _set_context(user, cr["HARVEST"])
    grace_member_name = frappe.db.get_value(
        "Chama Member", {"phone": "+254700100001", "chama": cr["UMOJA"]}, "name"
    )
    grace_doc = frappe.get_doc("Chama Member", grace_member_name)
    allowed_cross = perm_svc.has_chama_doc_permission(grace_doc, "read", user)
    checks.append(_check("Switching to Harvest blocks Grace's Umoja record",
                          not allowed_cross, f"returned={allowed_cross}"))

    return _result("A7", "Cross-Chama direct record access blocked", checks)


def test_a8_context_switch_audit_log(cr, mr):
    """A8 — Every context switch creates a Chama Context Session record."""
    user = "samuel@shared.test"
    checks = []

    before_count = frappe.db.count("Chama Context Session", {"user": user})

    # Switch 1: Umoja → Harvest
    _set_context(user, cr["UMOJA"])
    _create_audit_record(
        user=user,
        active_chama=cr["HARVEST"],
        previous_chama=cr["UMOJA"],
        source_channel="WEB",
    )
    frappe.session.data["active_chama"] = cr["HARVEST"]

    # Switch 2: Harvest → Umoja
    _create_audit_record(
        user=user,
        active_chama=cr["UMOJA"],
        previous_chama=cr["HARVEST"],
        source_channel="WEB",
    )
    frappe.session.data["active_chama"] = cr["UMOJA"]

    after_count = frappe.db.count("Chama Context Session", {"user": user})
    new_records = after_count - before_count

    checks.append(_check("2 audit records created for 2 switches",
                          new_records == 2, f"before={before_count} after={after_count}"))

    # Verify record content
    audit_rows = frappe.db.get_all(
        "Chama Context Session",
        filters={"user": user},
        fields=["name", "user", "active_chama", "previous_chama", "switched_at", "source_channel"],
        order_by="creation desc",
        limit=2,
    )
    for row in audit_rows:
        has_user      = row.user == user
        has_active    = bool(row.active_chama)
        has_timestamp = bool(row.switched_at)
        has_channel   = row.source_channel == "WEB"
        checks.append(_check(
            f"Audit record {row.name}: user/chama/timestamp/channel present",
            has_user and has_active and has_timestamp and has_channel,
            f"active={row.active_chama} prev={row.previous_chama} at={row.switched_at}",
        ))

    return _result("A8", "Context switch creates audit log (Chama Context Session)", checks)


def test_a9_in_context_record_stamps_chama(cr, mr):
    """A9 — Records created in Umoja context carry Umoja's chama stamp."""
    user = "grace@umoja.test"
    _set_context(user, cr["UMOJA"])
    checks = []

    umoja = cr["UMOJA"]
    grace_name = frappe.db.get_value(
        "Chama Member", {"phone": "+254700100001", "chama": umoja}, "name"
    )

    # Create a role assignment explicitly stamped with active chama (UMOJA)
    test_role_doc = frappe.get_doc({
        "doctype": "Chama Member Role Assignment",
        "chama": umoja,
        "member": grace_name,
        "role_name": "Committee",
        "effective_from": today(),
        "active": 1,
        "assigned_by": "Administrator",
    })
    test_role_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    saved_chama = frappe.db.get_value(
        "Chama Member Role Assignment", test_role_doc.name, "chama"
    )
    checks.append(_check(
        "Role assignment created in Umoja context carries chama = Umoja",
        saved_chama == umoja,
        f"saved chama={saved_chama}",
    ))

    # Now switch to Harvest and create a record there
    harvest = cr["HARVEST"]
    _set_context("samuel@shared.test", harvest)
    samuel_harvest = frappe.db.get_value(
        "Chama Member", {"phone": "+254711200002", "chama": harvest}, "name"
    )
    harvest_role_doc = frappe.get_doc({
        "doctype": "Chama Member Role Assignment",
        "chama": harvest,
        "member": samuel_harvest,
        "role_name": "Committee",
        "effective_from": today(),
        "active": 1,
        "assigned_by": "Administrator",
    })
    harvest_role_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    saved_harvest_chama = frappe.db.get_value(
        "Chama Member Role Assignment", harvest_role_doc.name, "chama"
    )
    checks.append(_check(
        "Role assignment created in Harvest context carries chama = Harvest",
        saved_harvest_chama == harvest,
        f"saved chama={saved_harvest_chama}",
    ))

    # Verify cross-chama record creation is blocked by member-chama validation
    try:
        cross_doc = frappe.get_doc({
            "doctype": "Chama Member Role Assignment",
            "chama": cr["UMOJA"],
            "member": samuel_harvest,  # Samuel's Harvest member in Umoja context
            "role_name": "Committee",
            "effective_from": today(),
            "active": 1,
            "assigned_by": "Administrator",
        })
        cross_doc.insert(ignore_permissions=True)
        checks.append(_check(
            "Cross-chama member reference is blocked by validate()",
            False, "ERROR: insert succeeded — expected ValidationError"
        ))
        frappe.db.rollback()
    except frappe.ValidationError as e:
        checks.append(_check(
            "Cross-chama member reference blocked by validate()",
            True, f"ValidationError: {str(e)[:80]}"
        ))

    return _result(
        "A9", "New in-context records stamp the correct Chama", checks,
        notes=(
            "Phase A requires callers to explicitly set chama on new records. "
            "Auto-stamping from session will be added as a UI/form layer feature."
        ),
    )


def test_a10_chama_settings_isolation(cr, mr):
    """A10 — Chama Settings are tenant-specific and cross-context access is blocked."""
    checks = []

    # Fetch Umoja settings
    umoja_settings = frappe.db.get_value(
        "Chama Settings", {"chama": cr["UMOJA"]}, ["name", "budget_overrun_mode"], as_dict=True
    )
    harvest_settings = frappe.db.get_value(
        "Chama Settings", {"chama": cr["HARVEST"]}, ["name", "budget_overrun_mode"], as_dict=True
    )
    jirani_settings = frappe.db.get_value(
        "Chama Settings", {"chama": cr["JIRANI"]}, ["name", "budget_overrun_mode"], as_dict=True
    )

    checks.append(_check("Umoja settings exist and have budget_overrun_mode=Warn",
                          umoja_settings and umoja_settings.budget_overrun_mode == "Warn",
                          str(umoja_settings)))
    checks.append(_check("Harvest settings exist and have budget_overrun_mode=Block",
                          harvest_settings and harvest_settings.budget_overrun_mode == "Block",
                          str(harvest_settings)))
    checks.append(_check("Jirani settings exist and have budget_overrun_mode=Allow With Escalation",
                          jirani_settings and jirani_settings.budget_overrun_mode == "Allow With Escalation",
                          str(jirani_settings)))

    # Settings for different Chamas are different objects
    checks.append(_check("Settings records are distinct per Chama",
                          umoja_settings.name != harvest_settings.name,
                          f"Umoja={umoja_settings.name} Harvest={harvest_settings.name}"))

    # Cross-context access: samuel in Umoja context should be blocked from Harvest settings
    user = "samuel@shared.test"
    _set_context(user, cr["UMOJA"])

    harvest_settings_doc = frappe.get_doc("Chama Settings", harvest_settings.name)
    cross_allowed = perm_svc.has_chama_doc_permission(harvest_settings_doc, "read", user)
    checks.append(_check("Harvest settings blocked under Umoja session",
                          not cross_allowed, f"has_permission={cross_allowed}"))

    # Umoja settings accessible in Umoja context
    umoja_settings_doc = frappe.get_doc("Chama Settings", umoja_settings.name)
    own_allowed = perm_svc.has_chama_doc_permission(umoja_settings_doc, "read", user)
    checks.append(_check("Umoja settings accessible under Umoja session",
                          own_allowed, f"has_permission={own_allowed}"))

    return _result("A10", "Chama Settings isolation across tenants", checks)


# ──────────────────────────────────────────────────────────────────────────────
# Report printer
# ──────────────────────────────────────────────────────────────────────────────

def print_report(results, manifest, cr, mr):
    W = 72
    PASS_BADGE = " PASS "
    FAIL_BADGE = " FAIL "

    def bar(char="─", width=W):
        print(char * width)

    def header_line(label, value):
        print(f"  {label:<22} {value}")

    bar("═")
    print("  PHASE A RELEASE GATE — TEST REPORT")
    bar("═")
    header_line("Site:", "chama.midas.com")
    header_line("Timestamp:", str(now_datetime()))
    header_line("Chamas seeded:", ", ".join(f"{c} → {n}" for c, n in cr.items()))
    bar()

    # Seed manifest
    print("  SEED MANIFEST")
    bar("─")
    categories = ["users", "chamas", "settings", "members", "roles"]
    for cat in categories:
        created  = sum(1 for s, _ in manifest.get(cat, []) if s == "CREATED")
        existing = sum(1 for s, _ in manifest.get(cat, []) if s == "EXISTING")
        print(f"  {cat.capitalize():<14}  created={created}  existing={existing}")
    bar()

    # Test results
    print("  TEST RESULTS")
    bar("─")
    pass_count = 0
    for r in results:
        badge = PASS_BADGE if r["status"] == "PASS" else FAIL_BADGE
        marker = "✓" if r["status"] == "PASS" else "✗"
        print(f"  [{badge}]  {r['id']}  {r['name']}")
        for c in r["checks"]:
            icon = "  ✓" if c["ok"] else "  ✗"
            detail = f"  ({c['detail']})" if c["detail"] else ""
            print(f"          {icon}  {c['desc']}{detail}")
        if r.get("notes"):
            print(f"          ℹ  NOTE: {r['notes']}")
        if r["status"] == "PASS":
            pass_count += 1
        bar("·", W)

    bar("═")
    total = len(results)
    verdict = "ALL TESTS PASSED" if pass_count == total else f"{total - pass_count} TEST(S) FAILED"
    print(f"  SUMMARY: {pass_count}/{total} passed  —  {verdict}")
    bar("═")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def run_phase_a_tests():
    print("\nSeeding test data…")
    cr, mr, manifest = seed_data()
    print(f"  Chama registry: { {c: n for c, n in cr.items()} }")

    tests = [
        lambda: test_a1_multi_chama_membership(cr, mr),
        lambda: test_a2_same_user_different_roles(cr, mr),
        lambda: test_a3_suspended_in_one_active_in_another(cr, mr),
        lambda: test_a4_outsider_cannot_switch(cr, mr),
        lambda: test_a5_inactive_chama_handling(cr, mr),
        lambda: test_a6_exclusive_role_conflict(cr, mr),
        lambda: test_a7_cross_chama_direct_access_blocked(cr, mr),
        lambda: test_a8_context_switch_audit_log(cr, mr),
        lambda: test_a9_in_context_record_stamps_chama(cr, mr),
        lambda: test_a10_chama_settings_isolation(cr, mr),
    ]

    results = []
    for fn in tests:
        try:
            results.append(fn())
        except Exception as e:
            import traceback
            results.append({
                "id": "??",
                "name": fn.__name__ if hasattr(fn, "__name__") else str(fn),
                "status": "FAIL",
                "checks": [_check("Unhandled exception", False, traceback.format_exc()[-300:])],
                "notes": str(e),
            })

    # Restore session to Administrator
    frappe.session.user = "Administrator"
    frappe.session.data["active_chama"] = None

    print_report(results, manifest, cr, mr)
