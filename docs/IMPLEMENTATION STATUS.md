# Chama Financial Operating Platform — Implementation Status

**System:** Nexus Finance / Chama Financial Operating Platform  
**Stack:** ERPNext v16 + Frappe v16 + Frappe Lending  
**App name:** `chama`  
**Site:** `chama.midas.com`  
**Last updated:** 2026-03-26 (after Phase A & B Hardening)

---

## Quick Summary

| Phase | Name | Status | Release Gate |
|-------|------|--------|-------------|
| A | Foundation | **Complete** | 10/10 passed |
| B | Contributions | **Complete** | 9/9 passed |
| A+B | Hardening | **Complete** | 6 gaps closed (see section below) |
| C | Loans (Frappe Lending integration) | Not started | — |
| D | Disbursements | Not started | — |
| E | Reconciliation Lite | Not started | — |
| F | Notifications Lite | Not started | — |
| G | Reports & Treasurer Dashboard | Not started | — |

---

## Phase A — Foundation

**Status: Complete**  
**Release gate: 10/10 passed**

### What was built

#### Module: `chama_core`

**DocTypes (5)**

| DocType | Autoname | Purpose |
|---------|----------|---------|
| Chama | `CH-.####` | Core tenant record — the Chama itself |
| Chama Settings | `field:chama` | Per-Chama configuration (budget overrun mode, etc.) |
| Chama Member | `MB-.####` | Member records within a Chama |
| Chama Member Role Assignment | `MRA-.####` | Time-bounded role assignments per member |
| Chama Context Session | `CCS-.####` | Immutable audit log for context switches |

**Services**

| File | Purpose |
|------|---------|
| `chama_core/services/permissions.py` | Central permission resolution — `get_active_chama_for_user`, `get_chama_member_for_user`, `get_effective_chama_roles`, `user_can_access_chama`, `user_has_chama_role`, `get_permission_query_conditions`, `has_chama_doc_permission` |
| `chama_core/utils/tenant.py` | Cross-Chama validation utilities — `ensure_same_chama`, `ensure_doc_matches_chama`, `ensure_member_matches_chama`, `get_member_for_user_in_chama` |

**APIs**

| File | Endpoint | Purpose |
|------|----------|---------|
| `chama_core/api/context.py` | `switch_active_chama` | Switches the active Chama for a user session; creates an audit record |
| `chama_core/api/responses.py` | Helpers | `success_response`, `error_response`, `validation_error_response` |

**Hooks wired**

- `after_install` → creates Module Def records on first install
- `permission_query_conditions` → tenant-scoped list filtering for all Chama DocTypes
- `has_permission` → record-level Chama scope check
- `scheduler_events` → scaffold registered (populated in Phase B)

### Key architectural decisions

- **Multi-tenancy is a security control, not a filter**: all queries include `chama` filter; violations raise `frappe.ValidationError`
- **Immutable audit log**: `Chama Context Session` cannot be modified after creation
- **Idempotent setup**: `after_install` uses existence checks, safe to re-run
- **Member status governs access**: only `Active` members can act; `Dormant`, `Suspended`, etc. are treated as inactive

### Test data (persistent)

| Group | Count | Key |
|-------|-------|-----|
| Frappe Users | 8 | email |
| Chamas | 3 (Umoja, Harvest, Jirani) | `chama_code` |
| Chama Settings | 3 | `chama` link |
| Chama Members | 8 | `phone` + `chama` |
| Role Assignments | 8 | `member` + `role_name` |

### Release gate scenarios (A1–A10)

| ID | Scenario | Result |
|----|----------|--------|
| A1 | Multi-Chama membership works | Pass |
| A2 | Same user, different roles per Chama | Pass |
| A3 | Suspended in one Chama, Active in another | Pass |
| A4 | Outsider cannot switch into any Chama | Pass |
| A5 | Inactive Chama / Dormant member handling | Pass |
| A6 | Exclusive role conflict warning | Pass |
| A7 | Cross-Chama direct record access blocked | Pass |
| A8 | Context switch creates audit log | Pass |
| A9 | New in-context record stamps correct Chama | Pass |
| A10 | Chama Settings isolation | Pass |

### Test files

| File | Purpose |
|------|---------|
| `chama_core/tests/seed.py` | Single source of truth for all test data; extended per phase |
| `chama_core/tests/test_phase_a.py` | `IntegrationTestCase` automated test suite |
| `chama_core/tests/phase_a_test_rig.py` | Standalone `bench execute` report runner |

---

## Phase B — Contributions

**Status: Complete**  
**Release gate: 9/9 passed**

### What was built

#### Module: `chama_contributions`

**DocTypes (5)**

| DocType | Autoname | Purpose |
|---------|----------|---------|
| Chama Contribution Category | `CCAT-.####` | Defines contribution types (Shares, Welfare, Levy, etc.) with amount rules and grace periods |
| Chama Contribution Cycle | `CYC-.####` | Groups obligations by period (monthly, quarterly, etc.) |
| Chama Contribution Obligation | `COB-.####` | Individual member payment obligations; tracks due/paid/waived/outstanding amounts |
| Chama Contribution Payment | `CPT-.####` | Payment events; carries allocation child rows and duplicate-reference detection |
| Contribution Payment Allocation | child table | Allocation rows linking a payment to specific obligations (`istable=1`) |

**Services**

| File | Key functions | Purpose |
|------|--------------|---------|
| `chama_contributions/services/allocation_engine.py` | `get_open_obligations`, `recompute_obligation_amounts_and_status`, `allocate_payment`, `reverse_payment_allocations` | Core financial logic — oldest-first allocation, reversal, status recomputation |
| `chama_contributions/services/cycle_generation.py` | `get_active_categories`, `get_eligible_members`, `resolve_category_amount`, `create_cycle`, `generate_obligations_for_cycle`, `generate_due_cycles_for_today` | Creates cycles and obligations on schedule; fully idempotent |
| `chama_contributions/services/obligation_status_jobs.py` | `refresh_due_statuses`, `refresh_overdue_statuses`, `apply_penalties_skeleton` | Daily jobs — Pending→Due, Due/Partially Paid→Overdue; penalties deferred to Phase C |

**APIs**

| File | Endpoint | Access rule |
|------|----------|------------|
| `chama_contributions/api/payments.py` | `submit_payment` | Authenticated + chama access + member-chama match; creates payment and triggers allocation |
| `chama_contributions/api/summary.py` | `get_member_contribution_summary` | Self or Chair/Treasurer/Auditor can read; System Manager bypasses member check |

**Reports (Script Reports, all chama-guarded)**

| Report | Filters |
|--------|---------|
| Contribution Compliance Report | Chama (reqd), Category, Cycle, Status |
| Overdue Contributions Report | Chama (reqd), Member, Date range |
| Payment Register | Chama (reqd), Member, Date range, Method |
| Member Contribution Statement | Chama (reqd), Member (reqd), Cycle, Category |

**Hooks wired**

- `permission_query_conditions` → added for all 4 new DocTypes
- `has_permission` → added for Obligation and Payment
- `scheduler_events.daily` → 4 jobs: `generate_due_cycles_for_today`, `refresh_due_statuses`, `refresh_overdue_statuses`, `apply_penalties_skeleton`

### Key architectural decisions

- **Allocation engine is the single source of truth** for all payment-to-obligation mapping; no inline calculations in APIs or controllers
- **Oldest-first ordering**: Overdue → Due → Partially Paid, then by due_date ascending
- **No wallet / credit**: unallocated payment remainder stays on the payment record; not carried forward
- **Terminal statuses (Paid, Waived, Cancelled)** are never touched by status jobs or the allocator
- **Idempotent cycle generation**: skips if cycle or obligation already exists for the same key tuple
- **Seed inserts with `Pending` then force-sets** final status via `frappe.db.set_value` to preserve exact test states without validate() interference
- **Platform admin bypass** in summary API: System Manager skips member-level access check

### Test data (persistent, extends Phase A)

| Group | Count | Seed key |
|-------|-------|---------|
| Contribution Categories | 5 (3 Umoja, 2 Harvest) | `(chama_code, category_code)` |
| Contribution Cycles | 3 (UMOJA-FEB-2026, UMOJA-MAR-2026, HARVEST-MAR-2026) | `(chama_code, cycle_name)` |
| Contribution Obligations | 20 (covering Paid, Partially Paid, Overdue, Due, Waived) | `(chama_code, phone, cycle_name, cat_code)` |
| Payments | 9 (U-001–U-007, H-001–H-002) — seeded as `Recorded` | `(chama_code, phone, payment_reference)` |

### Release gate scenarios (B1–B9)

| ID | Scenario | Result |
|----|----------|--------|
| B1 | Cross-Chama obligation creation raises `ValidationError` | Pass |
| B2 | Grace Feb full payment (6000) — 2 rows, both Paid, status Allocated | Pass |
| B3 | Samuel Feb Shares partial seed math — paid + outstanding = due | Pass |
| B4 | Samuel multi-obligation oldest-first (4000) — 3 rows, Overdue cleared first | Pass |
| B5 | Reversal of U-007 restores Grace levy outstanding to 2000 | Pass |
| B6 | Duplicate reference (U-006) — `duplicate_flag = 1` set | Pass |
| B7 | Linda Feb Welfare Waived stays Waived after status jobs | Pass |
| B8 | Summary API totals match raw DB obligation sums | Pass |
| B9 | Harvest isolation — Umoja payments have 0 allocation rows on Harvest obligations | Pass |

### Test files

| File | Purpose |
|------|---------|
| `chama_core/tests/seed.py` | Extended with `seed_phase_b()` — categories, cycles, obligations, payments |
| `chama_contributions/tests/test_phase_b.py` | `IntegrationTestCase` automated test suite (9 tests) |
| `chama_contributions/tests/phase_b_test_rig.py` | Standalone `bench execute` report runner |

### Running the test rigs

```bash
# Phase A
bench --site chama.midas.com execute \
  chama.chama_core.tests.phase_a_test_rig.run_phase_a_tests

# Phase B
bench --site chama.midas.com execute \
  chama.chama_contributions.tests.phase_b_test_rig.run_phase_b_tests

# Automated (both phases)
bench --site chama.midas.com run-tests --module chama.chama_core.tests.test_phase_a
bench --site chama.midas.com run-tests --module chama.chama_contributions.tests.test_phase_b
```

---

## Current File Inventory

```
apps/chama/chama/
├── hooks.py                              # App-level hooks — permissions, scheduler, install
├── modules.txt                           # Nexus Finance | Chama Core | Chama Contributions
│
├── chama_core/                           # Phase A — Foundation
│   ├── setup.py                          # after_install — registers Module Defs
│   ├── api/
│   │   ├── context.py                    # switch_active_chama API
│   │   └── responses.py                  # success_response / error_response / validation_error_response
│   ├── doctype/
│   │   ├── chama/                        # CH-.####
│   │   ├── chama_settings/               # field:chama
│   │   ├── chama_member/                 # MB-.####
│   │   ├── chama_member_role_assignment/ # MRA-.####
│   │   └── chama_context_session/        # CCS-.#### (immutable audit log)
│   ├── services/
│   │   └── permissions.py                # Chama-scoped permission resolution
│   ├── utils/
│   │   └── tenant.py                     # Cross-Chama validation utilities
│   └── tests/
│       ├── seed.py                       # Shared test data — Phase A + B
│       ├── test_phase_a.py               # IntegrationTestCase — 10 tests
│       └── phase_a_test_rig.py           # Standalone report runner
│
└── chama_contributions/                  # Phase B — Contributions
    ├── setup.py                          # ensure_module_def()
    ├── api/
    │   ├── payments.py                   # submit_payment
    │   └── summary.py                    # get_member_contribution_summary
    ├── doctype/
    │   ├── chama_contribution_category/  # CCAT-.####
    │   ├── chama_contribution_cycle/     # CYC-.####
    │   ├── chama_contribution_obligation/# COB-.####
    │   ├── chama_contribution_payment/   # CPT-.####
    │   └── contribution_payment_allocation/ # child table
    ├── services/
    │   ├── allocation_engine.py          # Core payment allocation logic
    │   ├── cycle_generation.py           # Cycle + obligation generation (scheduler)
    │   └── obligation_status_jobs.py     # Daily status transition jobs
    ├── report/
    │   ├── contribution_compliance_report/
    │   ├── overdue_contributions_report/
    │   ├── payment_register/
    │   └── member_contribution_statement/
    └── tests/
        ├── test_phase_b.py               # IntegrationTestCase — 9 tests
        └── phase_b_test_rig.py           # Standalone report runner
```

---

## Architectural Invariants (Always True)

1. Every record is tenant-scoped with a required `chama` Link field
2. Every API validates: authentication → Chama access → member-Chama match → input → state
3. All financial formulas live in dedicated service files — never inline in controllers or APIs
4. Every background job is idempotent — re-running produces no duplicates
5. Terminal financial states (Paid, Waived, Cancelled, Reversed) are write-once from a business-logic perspective
6. Reversals create compensating records — history is never overwritten
7. Loans are owned by Frappe Lending — the `chama_loans` module (Phase C) will wrap, not reimplement
8. Cross-Chama operations raise `frappe.ValidationError` at the service layer, not only in the UI

---

## Phase A & B Hardening

**Status: Complete**  
**Source:** Phase A & B Assessment (independent code review, scored 9.2/10)

Six actionable gaps identified by the assessment were closed in this hardening pass. Three items were consciously deferred (tracked in `docs/TECHNICAL DEBT.md`).

### What was fixed

| # | Gap | Fix |
|---|-----|-----|
| 1 | `allocate_payment()` did not block re-allocation of already-`Allocated` or `Flagged` payments | Added `PAYMENT_BLOCKED_STATUSES = ("Reversed", "Allocated", "Flagged")` guard |
| 2 | `_compute_status()` in `ChamaContributionObligation` demoted scheduler-set "Due"/"Overdue" to "Partially Paid" on save | Controller now only transitions to "Paid" (terminal); "Partially Paid" is exclusively the allocation engine's responsibility |
| 3 | No audit trail for financial events | Created `Chama Audit Log` DocType (`AUD-.####`, immutable) in `chama_core` |
| 4 | Payment allocations and reversals were unlogged | `allocate_payment()` and `reverse_payment_allocations()` each create one `Chama Audit Log` record |
| 5 | Bulk scheduler status jobs had no audit trail | `refresh_due_statuses()` and `refresh_overdue_statuses()` now create per-chama summary audit log records |
| 6 | `frappe.db.set_value` usages in seed and scheduler had no safety rationale | Added explicit docstring comments to both `seed_obligations()` and `obligation_status_jobs.py` explaining valid/invalid use |

### State machines now formally documented

The obligation and payment status lifecycles are now documented as module-level constants:

- `OBLIGATION_STATUS_MACHINE` in `chama_contribution_obligation.py` — maps each status to the actor that owns it (controller / scheduler / allocation engine / manual)
- `PAYMENT_STATUS_MACHINE` in `allocation_engine.py` (module docstring) — documents all valid and explicitly blocked transitions

### Chama Audit Log

| Field | Type | Purpose |
|-------|------|---------|
| `chama` | Link → Chama | Tenant scope |
| `event_type` | Select | Payment Allocated / Payment Reversed / Obligation Status Changed / Access Denied |
| `actor` | Link → User | Who triggered the event |
| `timestamp` | Datetime | When |
| `document_type` | Data | DocType of the affected record |
| `document_name` | Data | Name of the affected record |
| `summary` | Small Text | Human-readable one-liner |
| `before_state` | Long Text (JSON) | State snapshot before the change |
| `after_state` | Long Text (JSON) | State snapshot after the change |

### What stayed deferred

See `docs/TECHNICAL DEBT.md`:

| Item | Reason |
|------|--------|
| Concurrency / row-level locking | Assessment: "soon, not now" — address before Phase C |
| Fuzzy duplicate detection | Assessment: "not now" — address in Phase D or E |
| Penalty obligation system | Phase C/D scope — skeleton already in `apply_penalties_skeleton()` |

---

## What Comes Next

### Phase C — Loans (Frappe Lending integration)

The `chama_loans` module wraps **Frappe Lending**. It does not reimplement loan logic.

| Task | Artifact |
|------|---------|
| C-001 | Extend Lending Loan with custom fields: `chama`, `member`, `guarantor_status`, `eligibility_snapshot`, `approval_required_level`, `exception_flag` |
| C-002 | Chama Guarantor DocType |
| C-003 | Loan Eligibility Service |
| C-004 | Loan Application API (`chama.loan.apply`) |
| C-005 | Loan Approval Workflow (Submitted → Under Review → Approved / Rejected) |
| C-006 | Loan sync handler (disbursement + repayment visibility) |

**Gate:** Loan wrapper data matches Lending state; guarantor logic and eligibility snapshots are consistent.

### Phase D — Disbursements

Fully custom module.

| Task | Artifact |
|------|---------|
| D-001 | Chama Disbursement Request |
| D-002 | Chama Disbursement Execution |
| D-003 | Chama Approval Rule |
| D-004 | Chama Disbursement Reversal |
| D-005 | Execution service |
| D-006 | Reversal service |
| D-007 | Disbursement APIs + report |

**Gate:** Disbursement execution cannot duplicate; every execution has a traceable approved basis.

### Phase E — Reconciliation Lite

Depends on B + C + D being stable.

| Task | Artifact |
|------|---------|
| E-001 | Chama Financial Period |
| E-002 | Chama Reconciliation Run |
| E-003 | Reconciliation Source Balance (child table) |
| E-004 | Expected Balance Engine |
| E-005 | Chama Reconciliation Issue |
| E-006 | Reconciliation API + report |

### Phase F — Notifications Lite

| Task | Artifact |
|------|---------|
| F-001 | Chama Notification Event |
| F-002 | Chama Notification Queue |
| F-003 | Chama Notification Inbox |
| F-004 | Queue processor + retry jobs |
| F-005 | Event trigger integrations (contribution due/overdue, loan approved, disbursement executed) |

### Phase G — Reports & Treasurer Dashboard

| Task | Artifact |
|------|---------|
| G-001 | Member Statement API |
| G-002 | Contribution Compliance Report |
| G-003 | Loan Portfolio Report |
| G-004 | Disbursement Register |
| G-005 | Reconciliation Summary Report |
| G-006 | Treasurer Dashboard |

---

## TDD Convention (Established in Phase A, Extended Each Phase)

All phases follow the same testing pattern:

1. **`chama_core/tests/seed.py`** — single source of truth for all test data across all phases; each phase adds a `seed_phase_X()` function; `seed_data()` calls them all
2. **`<module>/tests/test_phase_X.py`** — `IntegrationTestCase` tests; seed data committed once in `setUpClass`; individual test mutations rolled back by savepoint
3. **`<module>/tests/phase_X_test_rig.py`** — standalone `bench execute` script; seeds data, runs all tests, prints a formatted pass/fail report

**Seed key convention:**

| Data type | Idempotency key |
|-----------|----------------|
| Chama | `chama_code` |
| Member | `(chama_code, phone)` |
| Category | `(chama_code, category_code)` |
| Cycle | `(chama_code, cycle_name)` |
| Obligation | `(chama_code, phone, cycle_name, category_code)` |
| Payment | `(chama_code, phone, payment_reference)` or `date + amount` for Cash |
