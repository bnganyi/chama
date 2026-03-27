"""
Testing UI Workspaces — Frappe v16

Provisions all internal QA/developer workspaces and number cards.
These are temporary testing scaffolds and are NOT production UX.

Usage:
    bench --site chama.midas.com execute \
        chama.chama_core.setup.workspace_setup.setup_testing_workspaces

Re-running is safe: workspaces are deleted and recreated; number cards are skipped
if they already exist.
"""

import json

import frappe
from frappe.utils import now_datetime


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def setup_testing_workspaces():
    """Create or refresh all testing workspaces and number cards."""
    _setup_number_cards()

    # sequence_id controls sidebar ordering; start at 10 to stay ahead of
    # ERPNext built-in workspaces which typically use lower values.
    _upsert_workspace("Nexus QA Home",      _nexus_qa_home_def(),   sequence_id=10)
    _upsert_workspace("Foundation",         _foundation_def(),       sequence_id=11)
    _upsert_workspace("Contributions",      _contributions_def(),    sequence_id=12)
    _upsert_workspace("Reports",            _reports_def(),          sequence_id=13)
    _upsert_workspace("Test Utilities",     _test_utilities_def(),   sequence_id=14)

    shells = [
        ("Loans (Phase C)",        15),
        ("Disbursements (Phase D)", 16),
        ("Reconciliation (Phase E)", 17),
        ("Notifications (Phase F)", 18),
    ]
    for shell_name, seq in shells:
        _upsert_workspace(shell_name, _shell_def(shell_name), sequence_id=seq)

    frappe.db.commit()
    print("✓ Testing workspaces provisioned.")


# ──────────────────────────────────────────────────────────────────────────────
# Infrastructure helpers
# ──────────────────────────────────────────────────────────────────────────────

def _upsert_workspace(name, defn, sequence_id=10):
    """Delete existing workspace by name, then create fresh from defn."""
    if frappe.db.exists("Workspace", name):
        frappe.delete_doc("Workspace", name, ignore_missing=True, force=True)
        frappe.db.commit()

    doc = frappe.get_doc({
        "doctype": "Workspace",
        "name": name,
        "label": name,
        "title": name,
        "public": 1,
        "is_hidden": 0,
        "sequence_id": sequence_id,
        "module": defn.get("module", "Chama Core"),
        "content": json.dumps(defn["content"]),
        "shortcuts": defn.get("shortcuts", []),
        "number_cards": defn.get("number_cards", []),
    })
    # Ignore link validation: workspaces may reference each other or future
    # DocTypes that don't exist yet in this site.
    doc.flags.ignore_links = True
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    print(f"  workspace: {name}")


def _upsert_number_card(label, doc_type, filters, function="Count", agg_field=None):
    """Create Number Card; skip if already exists."""
    if frappe.db.exists("Number Card", label):
        return
    card = {
        "doctype": "Number Card",
        "name": label,
        "label": label,
        "type": "Document Type",
        "document_type": doc_type,
        "function": function,
        "filters_json": json.dumps(filters),
        "is_public": 0,
        "show_percentage_stats": 0,
    }
    if agg_field:
        card["aggregate_function_based_on"] = agg_field
    frappe.get_doc(card).insert(ignore_permissions=True)
    print(f"  number card: {label}")


# ──────────────────────────────────────────────────────────────────────────────
# Content block factories
# ──────────────────────────────────────────────────────────────────────────────

_id_counter = [0]


def _uid():
    _id_counter[0] += 1
    return f"blk{_id_counter[0]:04d}"


def _header(text):
    return {"id": _uid(), "type": "header",
            "data": {"text": f'<span class="h4"><b>{text}</b></span>', "col": 12}}


def _spacer():
    return {"id": _uid(), "type": "spacer", "data": {"col": 12}}


def _sc(label):
    """Shortcut content block — references a shortcut row by its label."""
    return {"id": _uid(), "type": "shortcut", "data": {"shortcut_name": label, "col": 3}}


def _nc(card_label):
    """Number card content block."""
    return {"id": _uid(), "type": "number_card",
            "data": {"number_card_name": card_label, "col": 3}}


# ──────────────────────────────────────────────────────────────────────────────
# Shortcut row factories
# ──────────────────────────────────────────────────────────────────────────────

def _dt_sc(label, doctype, icon=None):
    """DocType shortcut row."""
    row = {"label": label, "type": "DocType", "link_to": doctype}
    if icon:
        row["icon"] = icon
    return row


def _report_sc(label, report_name):
    """Report shortcut row."""
    return {"label": label, "type": "Report", "link_to": report_name,
            "report_ref_doctype": "Chama Contribution Obligation"}


def _url_sc(label, url, icon=None):
    """URL shortcut row (used for filtered views and workspace nav)."""
    row = {"label": label, "type": "URL", "url": url}
    if icon:
        row["icon"] = icon
    return row


def _ws_sc(label, workspace_name):
    """Shortcut to another workspace via URL (Workspace is not a valid shortcut type in v16)."""
    slug = workspace_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
    return {"label": label, "type": "URL", "url": f"/app/{slug}"}


def _nc_row(card_label):
    """Number card child table row for the workspace."""
    return {"card_name": card_label}


# ──────────────────────────────────────────────────────────────────────────────
# Number Cards
# ──────────────────────────────────────────────────────────────────────────────

def _setup_number_cards():
    _upsert_number_card(
        "Active Chamas", "Chama",
        [["Chama", "status", "=", "Active"]],
    )
    _upsert_number_card(
        "Active Members", "Chama Member",
        [["Chama Member", "status", "=", "Active"]],
    )
    _upsert_number_card(
        "Suspended Members", "Chama Member",
        [["Chama Member", "status", "=", "Suspended"]],
    )
    _upsert_number_card(
        "Dormant Members", "Chama Member",
        [["Chama Member", "status", "=", "Dormant"]],
    )
    _upsert_number_card(
        "Open Contribution Obligations", "Chama Contribution Obligation",
        [["Chama Contribution Obligation", "status", "in",
          "Due,Overdue,Partially Paid,Pending"]],
    )
    _upsert_number_card(
        "Overdue Contribution Obligations", "Chama Contribution Obligation",
        [["Chama Contribution Obligation", "status", "=", "Overdue"]],
    )
    _upsert_number_card(
        "Payments Today", "Chama Contribution Payment",
        [["Chama Contribution Payment", "payment_date", "=", "Today"]],
    )
    _upsert_number_card(
        "Flagged Payments", "Chama Contribution Payment",
        [["Chama Contribution Payment", "duplicate_flag", "=", 1]],
    )
    _upsert_number_card(
        "Total Outstanding Contributions", "Chama Contribution Obligation",
        [["Chama Contribution Obligation", "status", "not in",
          "Paid,Waived,Cancelled"]],
        function="Sum",
        agg_field="amount_outstanding",
    )
    frappe.db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# Workspace definitions
# ──────────────────────────────────────────────────────────────────────────────

def _nexus_qa_home_def():
    shortcuts = [
        # Build Status — workspace nav
        _ws_sc("Foundation", "Foundation"),
        _ws_sc("Contributions", "Contributions"),
        _ws_sc("Reports", "Reports"),
        _ws_sc("Test Utilities", "Test Utilities"),
        _ws_sc("Loans (Phase C)", "Loans (Phase C)"),
        _ws_sc("Disbursements (Phase D)", "Disbursements (Phase D)"),
        _ws_sc("Reconciliation (Phase E)", "Reconciliation (Phase E)"),
        _ws_sc("Notifications (Phase F)", "Notifications (Phase F)"),
        # Core Master Data
        _dt_sc("Chama", "Chama"),
        _dt_sc("Chama Settings", "Chama Settings"),
        _dt_sc("Chama Member", "Chama Member"),
        _dt_sc("Chama Member Role Assignment", "Chama Member Role Assignment"),
        # Financial Engine
        _dt_sc("Contribution Category", "Chama Contribution Category"),
        _dt_sc("Contribution Cycle", "Chama Contribution Cycle"),
        _dt_sc("Contribution Obligation", "Chama Contribution Obligation"),
        _dt_sc("Contribution Payment", "Chama Contribution Payment"),
        # Reports
        _report_sc("Compliance Report", "Contribution Compliance Report"),
        _report_sc("Overdue Report", "Overdue Contributions Report"),
        _report_sc("Payment Register", "Payment Register"),
        _report_sc("Member Statement", "Member Contribution Statement"),
        # Recent Activity
        _url_sc("Recent Payments",
                "/app/chama-contribution-payment?order_by=creation+desc"),
        _url_sc("Recent Context Switches",
                "/app/chama-context-session?order_by=switched_at+desc"),
        _url_sc("Recent Obligations",
                "/app/chama-contribution-obligation?order_by=creation+desc"),
        _url_sc("Recently Created Members",
                "/app/chama-member?order_by=creation+desc"),
    ]

    content = [
        _header("Build Status — Workspaces"),
        _sc("Foundation"), _sc("Contributions"), _sc("Reports"), _sc("Test Utilities"),
        _sc("Loans (Phase C)"), _sc("Disbursements (Phase D)"),
        _sc("Reconciliation (Phase E)"), _sc("Notifications (Phase F)"),
        _spacer(),
        _header("Core Master Data"),
        _sc("Chama"), _sc("Chama Settings"), _sc("Chama Member"),
        _sc("Chama Member Role Assignment"),
        _spacer(),
        _header("Current Financial Engine"),
        _sc("Contribution Category"), _sc("Contribution Cycle"),
        _sc("Contribution Obligation"), _sc("Contribution Payment"),
        _spacer(),
        _header("Quick Reports"),
        _sc("Compliance Report"), _sc("Overdue Report"),
        _sc("Payment Register"), _sc("Member Statement"),
        _spacer(),
        _header("Health Snapshot"),
        _nc("Active Chamas"), _nc("Active Members"), _nc("Suspended Members"),
        _nc("Open Contribution Obligations"),
        _nc("Overdue Contribution Obligations"), _nc("Payments Today"),
        _spacer(),
        _header("Recent Activity"),
        _sc("Recent Payments"), _sc("Recent Context Switches"),
        _sc("Recent Obligations"), _sc("Recently Created Members"),
    ]

    return {"shortcuts": shortcuts, "content": content, "module": "Chama Core"}


def _foundation_def():
    shortcuts = [
        # Master Tenant Setup
        _dt_sc("Chama", "Chama"),
        _dt_sc("Chama Settings", "Chama Settings"),
        # Membership
        _dt_sc("Chama Member", "Chama Member"),
        _dt_sc("Chama Member Role Assignment", "Chama Member Role Assignment"),
        # Tenant Audit
        _dt_sc("Chama Context Session", "Chama Context Session"),
        _dt_sc("Chama Audit Log", "Chama Audit Log"),
        # Filtered Views
        _url_sc("Active Chamas", "/app/chama?status=Active"),
        _url_sc("Inactive Chamas", "/app/chama?status=Inactive"),
        _url_sc("Active Members", "/app/chama-member?status=Active"),
        _url_sc("Suspended Members", "/app/chama-member?status=Suspended"),
        _url_sc("Dormant Members", "/app/chama-member?status=Dormant"),
        # Release Gate
        _url_sc("Test A1 — Multi-Chama Membership",
                "/app/chama-member?order_by=creation+desc"),
        _url_sc("Test A2 — Role by Chama",
                "/app/chama-member-role-assignment?order_by=creation+desc"),
        _url_sc("Test A3 — Suspended vs Active",
                "/app/chama-member?status=Suspended"),
        _url_sc("Test A4 — Outsider Access Denied",
                "/app/chama-audit-log?event_type=Access+Denied"),
        _url_sc("Test A7 — Cross-Chama Record Access",
                "/app/chama-audit-log?order_by=timestamp+desc"),
        _url_sc("Test A8 — Context Audit",
                "/app/chama-context-session?order_by=switched_at+desc"),
    ]

    number_cards = [
        _nc_row("Active Chamas"),
        _nc_row("Active Members"),
        _nc_row("Suspended Members"),
        _nc_row("Dormant Members"),
    ]

    content = [
        _header("Master Tenant Setup"),
        _sc("Chama"), _sc("Chama Settings"),
        _spacer(),
        _header("Membership"),
        _sc("Chama Member"), _sc("Chama Member Role Assignment"),
        _spacer(),
        _header("Tenant Audit"),
        _sc("Chama Context Session"), _sc("Chama Audit Log"),
        _spacer(),
        _header("Useful Filtered Views"),
        _sc("Active Chamas"), _sc("Inactive Chamas"),
        _sc("Active Members"), _sc("Suspended Members"), _sc("Dormant Members"),
        _spacer(),
        _header("Health Snapshot"),
        _nc("Active Chamas"), _nc("Active Members"),
        _nc("Suspended Members"), _nc("Dormant Members"),
        _spacer(),
        _header("Release Gate Panel — Phase A"),
        _sc("Test A1 — Multi-Chama Membership"),
        _sc("Test A2 — Role by Chama"),
        _sc("Test A3 — Suspended vs Active"),
        _sc("Test A4 — Outsider Access Denied"),
        _sc("Test A7 — Cross-Chama Record Access"),
        _sc("Test A8 — Context Audit"),
    ]

    return {
        "shortcuts": shortcuts,
        "content": content,
        "number_cards": number_cards,
        "module": "Chama Core",
    }


def _contributions_def():
    shortcuts = [
        # Setup
        _dt_sc("Contribution Category", "Chama Contribution Category"),
        _dt_sc("Contribution Cycle", "Chama Contribution Cycle"),
        # Transactions
        _dt_sc("Contribution Obligation", "Chama Contribution Obligation"),
        _dt_sc("Contribution Payment", "Chama Contribution Payment"),
        # Reports
        _report_sc("Compliance Report", "Contribution Compliance Report"),
        _report_sc("Overdue Report", "Overdue Contributions Report"),
        _report_sc("Payment Register", "Payment Register"),
        _report_sc("Member Statement", "Member Contribution Statement"),
        # Filtered Obligations
        _url_sc("Due Obligations",
                "/app/chama-contribution-obligation?status=Due"),
        _url_sc("Overdue Obligations",
                "/app/chama-contribution-obligation?status=Overdue"),
        _url_sc("Partially Paid Obligations",
                "/app/chama-contribution-obligation?status=Partially+Paid"),
        _url_sc("Paid Obligations",
                "/app/chama-contribution-obligation?status=Paid"),
        _url_sc("Waived Obligations",
                "/app/chama-contribution-obligation?status=Waived"),
        # Filtered Payments
        _url_sc("Recorded Payments",
                "/app/chama-contribution-payment?status=Recorded"),
        _url_sc("Allocated Payments",
                "/app/chama-contribution-payment?status=Allocated"),
        _url_sc("Partially Allocated Payments",
                "/app/chama-contribution-payment?status=Partially+Allocated"),
        _url_sc("Flagged Payments",
                "/app/chama-contribution-payment?duplicate_flag=1"),
        _url_sc("Reversed Payments",
                "/app/chama-contribution-payment?status=Reversed"),
        # Seed/Test Scenarios
        _url_sc("Grace Feb Obligations",
                "/app/chama-contribution-obligation?"
                "member=grace%40umoja.test&order_by=due_date+asc"),
        _url_sc("Samuel Umoja Obligations",
                "/app/chama-contribution-obligation?"
                "member=samuel%40shared.test&order_by=due_date+asc"),
        _url_sc("Linda Waived Obligation",
                "/app/chama-contribution-obligation?status=Waived"),
        _url_sc("Grace Levy Payment",
                "/app/chama-contribution-payment?order_by=payment_date+desc"),
        _url_sc("Duplicate Payment Reference Checks",
                "/app/chama-contribution-payment?duplicate_flag=1"),
        _url_sc("Harvest Samuel Obligations",
                "/app/chama-contribution-obligation?order_by=creation+desc"),
        # Recent Operational
        _url_sc("Recent Payments",
                "/app/chama-contribution-payment?order_by=creation+desc"),
        _url_sc("Recent Obligations",
                "/app/chama-contribution-obligation?order_by=creation+desc"),
        _url_sc("Overdue Sorted by Due Date",
                "/app/chama-contribution-obligation?"
                "status=Overdue&order_by=due_date+asc"),
        _url_sc("Payments Missing Reference",
                "/app/chama-contribution-payment?"
                "payment_reference=&payment_method!=Cash"),
    ]

    number_cards = [
        _nc_row("Open Contribution Obligations"),
        _nc_row("Overdue Contribution Obligations"),
        _nc_row("Payments Today"),
        _nc_row("Flagged Payments"),
        _nc_row("Total Outstanding Contributions"),
    ]

    content = [
        _header("Setup"),
        _sc("Contribution Category"), _sc("Contribution Cycle"),
        _spacer(),
        _header("Transactions"),
        _sc("Contribution Obligation"), _sc("Contribution Payment"),
        _spacer(),
        _header("Reports"),
        _sc("Compliance Report"), _sc("Overdue Report"),
        _sc("Payment Register"), _sc("Member Statement"),
        _spacer(),
        _header("Filtered Action Views — Obligations"),
        _sc("Due Obligations"), _sc("Overdue Obligations"),
        _sc("Partially Paid Obligations"), _sc("Paid Obligations"),
        _sc("Waived Obligations"),
        _spacer(),
        _header("Filtered Action Views — Payments"),
        _sc("Recorded Payments"), _sc("Allocated Payments"),
        _sc("Partially Allocated Payments"),
        _sc("Flagged Payments"), _sc("Reversed Payments"),
        _spacer(),
        _header("Number Cards"),
        _nc("Open Contribution Obligations"),
        _nc("Overdue Contribution Obligations"),
        _nc("Payments Today"), _nc("Flagged Payments"),
        _nc("Total Outstanding Contributions"),
        _spacer(),
        _header("Seed / Test Scenarios — Phase B"),
        _sc("Grace Feb Obligations"), _sc("Samuel Umoja Obligations"),
        _sc("Linda Waived Obligation"), _sc("Grace Levy Payment"),
        _sc("Duplicate Payment Reference Checks"), _sc("Harvest Samuel Obligations"),
        _spacer(),
        _header("Recent Operational Lists"),
        _sc("Recent Payments"), _sc("Recent Obligations"),
        _sc("Overdue Sorted by Due Date"), _sc("Payments Missing Reference"),
    ]

    return {
        "shortcuts": shortcuts,
        "content": content,
        "number_cards": number_cards,
        "module": "Chama Contributions",
    }


def _reports_def():
    shortcuts = [
        # Contribution Reports
        _report_sc("Compliance Report", "Contribution Compliance Report"),
        _report_sc("Overdue Report", "Overdue Contributions Report"),
        _report_sc("Payment Register", "Payment Register"),
        _report_sc("Member Statement", "Member Contribution Statement"),
        # Foundation/Admin — placeholders (URL type pointing to list)
        _url_sc("Multi-Chama Access Report (Planned)",
                "/app/chama-member?order_by=chama+asc"),
        _url_sc("Membership Status Report (Planned)",
                "/app/chama-member?order_by=status+asc"),
        _url_sc("Role Assignment History (Planned)",
                "/app/chama-member-role-assignment?order_by=effective_from+desc"),
        # Comparison / QA Links
        _url_sc("Compare Summary API vs Compliance Report",
                "/app/query-report/Contribution%20Compliance%20Report"),
        _url_sc("Compare Payment Register vs Payment List",
                "/app/chama-contribution-payment?order_by=creation+desc"),
        _url_sc("Compare Member Statement vs Obligation List",
                "/app/chama-contribution-obligation?order_by=creation+desc"),
        # Reporting Utilities
        _url_sc("Saved Reports", "/app/report"),
        _url_sc("Favorites", "/app/user"),
        _url_sc("Report Debug / Validation (Placeholder)", "/app/report"),
    ]

    content = [
        _header("Contribution Reports"),
        _sc("Compliance Report"), _sc("Overdue Report"),
        _sc("Payment Register"), _sc("Member Statement"),
        _spacer(),
        _header("Foundation / Admin Reports (Planned)"),
        _sc("Multi-Chama Access Report (Planned)"),
        _sc("Membership Status Report (Planned)"),
        _sc("Role Assignment History (Planned)"),
        _spacer(),
        _header("Comparison / QA Links"),
        _sc("Compare Summary API vs Compliance Report"),
        _sc("Compare Payment Register vs Payment List"),
        _sc("Compare Member Statement vs Obligation List"),
        _spacer(),
        _header("Reporting Utilities"),
        _sc("Saved Reports"), _sc("Favorites"),
        _sc("Report Debug / Validation (Placeholder)"),
    ]

    return {"shortcuts": shortcuts, "content": content, "module": "Chama Core"}


def _test_utilities_def():
    shortcuts = [
        # Seed / Test References
        _url_sc("Phase A Seed Reference",
                "/app/chama-member?order_by=creation+asc"),
        _url_sc("Phase B Seed Reference",
                "/app/chama-contribution-obligation?order_by=creation+asc"),
        _url_sc("Phase A Test Rig",
                "/app/chama-context-session?order_by=switched_at+desc"),
        _url_sc("Phase B Test Rig",
                "/app/chama-contribution-payment?order_by=creation+desc"),
        # Diagnostics
        _url_sc("Flagged Payments",
                "/app/chama-contribution-payment?duplicate_flag=1"),
        _url_sc("Suspended Members",
                "/app/chama-member?status=Suspended"),
        _url_sc("Cross-Chama Audit Logs",
                "/app/chama-audit-log?order_by=timestamp+desc"),
        _url_sc("Context Sessions Today",
                "/app/chama-context-session?order_by=switched_at+desc"),
        # Integrity Checks
        _url_sc("Duplicate Payment References",
                "/app/chama-contribution-payment?duplicate_flag=1"),
        _url_sc("Orphan Role Assignments",
                "/app/chama-member-role-assignment?active=0"),
        _url_sc("Payments Missing Reference",
                "/app/chama-contribution-payment?payment_reference="),
        _url_sc("Mismatched Member/Chama Links",
                "/app/chama-member?order_by=chama+asc"),
        # Developer Notes
        _url_sc("Current Test Commands",
                "/app/chama-audit-log?order_by=timestamp+desc"),
        _url_sc("Current Release Gate Status",
                "/app/chama-audit-log?event_type=Obligation+Status+Changed"),
        _url_sc("Known Issues",
                "/app/chama-audit-log?event_type=Access+Denied"),
        _url_sc("Next Phase Tasks",
                "/app/chama?status=Active"),
    ]

    content = [
        _header("Seed / Test References"),
        _sc("Phase A Seed Reference"), _sc("Phase B Seed Reference"),
        _sc("Phase A Test Rig"), _sc("Phase B Test Rig"),
        _spacer(),
        _header("Diagnostics"),
        _sc("Flagged Payments"), _sc("Suspended Members"),
        _sc("Cross-Chama Audit Logs"), _sc("Context Sessions Today"),
        _spacer(),
        _header("Integrity Checks"),
        _sc("Duplicate Payment References"), _sc("Orphan Role Assignments"),
        _sc("Payments Missing Reference"), _sc("Mismatched Member/Chama Links"),
        _spacer(),
        _header("Developer Notes"),
        _sc("Current Test Commands"), _sc("Current Release Gate Status"),
        _sc("Known Issues"), _sc("Next Phase Tasks"),
    ]

    return {"shortcuts": shortcuts, "content": content, "module": "Chama Core"}


# Planned artifacts per shell workspace
_SHELL_ARTIFACTS = {
    "Loans (Phase C)": [
        ("Loan List (Planned)", "/app/loan"),
        ("Chama Guarantor (Planned)", "/app/chama"),
        ("Loan Portfolio Report (Planned)", "/app/report"),
        ("Overdue Loans Report (Planned)", "/app/report"),
    ],
    "Disbursements (Phase D)": [
        ("Disbursement Request (Planned)", "/app/chama"),
        ("Disbursement Execution (Planned)", "/app/chama"),
        ("Disbursement Register (Planned)", "/app/report"),
    ],
    "Reconciliation (Phase E)": [
        ("Financial Period (Planned)", "/app/chama"),
        ("Reconciliation Run (Planned)", "/app/chama"),
        ("Reconciliation Issue (Planned)", "/app/chama"),
        ("Reconciliation Summary (Planned)", "/app/report"),
    ],
    "Notifications (Phase F)": [
        ("Notification Event (Planned)", "/app/chama"),
        ("Notification Queue (Planned)", "/app/chama"),
        ("Notification Inbox (Planned)", "/app/chama"),
        ("Notification Failures (Planned)", "/app/chama"),
    ],
}


def _shell_def(name):
    artifacts = _SHELL_ARTIFACTS.get(name, [])
    shortcuts = [_url_sc(label, url) for label, url in artifacts]
    shortcuts.append(_url_sc("Phase Status — Not Started", "/app/chama"))

    content = [
        _header(name),
        _spacer(),
        _header("Planned Artifacts"),
        *[_sc(label) for label, _ in artifacts],
        _spacer(),
        _header("Phase Status"),
        _sc("Phase Status — Not Started"),
    ]

    return {"shortcuts": shortcuts, "content": content, "module": "Chama Core"}
