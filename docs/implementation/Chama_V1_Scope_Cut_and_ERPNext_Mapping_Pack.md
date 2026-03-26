# Chama Platform — V1 Scope Cut  
and ERPNext Mapping Pack

ERPNext v16 / Frappe / Frappe Lending  
Implementation handoff for Cursor-based development

|     |     |
| --- | --- |
| Document Purpose | Define the minimum viable release that is safe to build first, and map that release into concrete ERPNext/Frappe implementation artifacts. |
| Recommended Build Order | Foundation → Contributions → Loans → Disbursements → Reconciliation Lite → Notifications Lite → Core Reports |
| Primary Audience | Founder / Product owner / ERPNext-Frappe developers using Cursor |

# 1\. Executive recommendation

The right sequence is to trim the platform to a coherent v1 first, then map only that v1 into ERPNext/Frappe implementation artifacts. Building the full master PRD directly in Cursor would create too much code before foundational decisions are stabilized.

Recommended approach: build a financial-operational v1 that proves tenant isolation, member identity, contribution flows, loan lifecycle integration, controlled disbursements, and basic reconciliation. Governance, budgeting, investments, and advanced analytics should follow only after the operational core is stable.

# 2\. V1 release goal

Deliver a production-credible first release that allows a Chama to onboard members, collect contributions, manage loans through Frappe Lending, execute controlled payouts, and verify expected versus actual balances without cross-tenant leakage.

# 3\. V1 scope boundary

## 3.1 Included in v1

- Multi-Chama foundation and Chama-scoped permissions
- Member lifecycle core: member records, basic role assignment, status management
- Contributions engine: categories, cycles, obligations, payments, allocations, overdue logic
- Loans layer: ERPNext Lending integration with Chama wrapper fields, eligibility snapshot, guarantors, approval flow
- Disbursements core: request, approval, execution, reversal
- Reconciliation Lite: expected balance, actual balance capture, variance, simple issue logging
- Notifications Lite: in-app inbox plus SMS for critical events
- Core reports and dashboards needed to operate v1 safely

## 3.2 Explicitly deferred to v2+

- Meetings and published minutes workflow
- Voting and resolution engine
- Budgeting with full line-item enforcement
- Investment ownership, valuation, returns, and exit liquidity handling
- Advanced analytics, trend packs, and metric cache optimization
- Platform admin diagnostics beyond minimal support tooling
- Complex member onboarding governance and advanced constitutional rules

## 3.3 Non-negotiables for v1

- Strict Chama isolation
- No duplicate financial posting path
- No silent edits to historical financial truth
- All state-changing actions auditable
- All key financial reports reconcile to source records
- Member-facing views only show authorized data

# 4\. V1 feature pack

## Foundation / platform controls

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Chama | Tenant master with code, status, base currency, timezone, settings reference |
| Chama Settings | Per-tenant operational defaults used by v1 modules |
| Chama context switching | User explicitly selects active Chama in web/mobile |
| Tenant-safe query enforcement | All tenant-owned records filtered by current Chama |
| Audit scaffolding | Foundational logging for role changes, approvals, reversals, and exports |

## Member lifecycle core

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Chama Member | Core member profile per tenant |
| Role assignment | Chair, Treasurer, Secretary, Auditor, Member |
| Status engine | Pending, Active, Suspended, Dormant, Exit In Progress, Exited |
| Application handling | Direct admin creation or simple approval path |
| Basic exit skeleton | Exit request and settlement placeholders, but no investment complexity yet |

## Contributions

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Contribution Category | Fixed/variable recurring and ad hoc categories |
| Contribution Cycle | Period generation batch |
| Contribution Obligation | Expected amount per member/category/period |
| Contribution Payment | Recorded receipt event |
| Allocation table | Deterministic allocation to obligations |
| Overdue/penalty baseline | Daily refresh plus basic penalty support |
| Member contribution statement | Self-service visibility |

## Loans

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Frappe Lending Loan extension | Custom fields for Chama, member, guarantor status, eligibility snapshot |
| Chama Guarantor | Guarantor commitments and sufficiency tracking |
| Eligibility snapshot | Stored at submission time |
| Approval routing | Treasurer/chair review on top of Lending |
| Borrower and officer views | Loan status, due dates, and review queues |

## Disbursements

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Disbursement Request | Request basis, beneficiary, approval state |
| Disbursement Execution | Actual payout event |
| Approval rules | Threshold-based routing |
| Reversal flow | Compensating record only |
| Beneficiary history | Member-facing payout visibility |

## Reconciliation Lite

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Financial Period | Lightweight period structure |
| Reconciliation Run | Expected vs actual comparison |
| Source balance capture | Bank/mobile/cash actual balances |
| Variance output | Simple discrepancy computation |
| Issue logging | Basic issue creation for unresolved differences |

## Notifications Lite

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Notification Event | Source modules emit events |
| Queue and inbox | In-app delivery and read state |
| Critical SMS | Contribution due/overdue, loan approval/overdue, payout execution |
| Template basics | Minimal active templates for v1 events |

## Core reports & dashboards

|     |     |
| --- | --- |
| **Artifact** | **Minimum v1 requirement** |
| Member Statement | Contribution + loan + disbursement overview |
| Contribution Compliance | By member/category |
| Loan Portfolio | Borrower and balance visibility |
| Disbursement Register | Money-out control |
| Reconciliation Summary | Expected vs actual |
| Treasurer dashboard | Small but operationally meaningful KPI set |

# 5\. Recommended build order

|     |     |     |     |
| --- | --- | --- | --- |
| **Step** | **Workstream** | **Why it must come now** | **Release gate** |
| 1   | Foundation | All modules depend on Chama scope, member identity, and role enforcement. | No cross-tenant leakage |
| 2   | Contributions | Provides savings engine and loan eligibility foundation. | Correct obligation/payment math |
| 3   | Loans | Uses Lending but depends on member and contribution truth. | Eligibility and guarantors proven |
| 4   | Disbursements | Completes money-out control and connects to loans. | No duplicate execution |
| 5   | Reconciliation Lite | Validates that financial backbone produces coherent balances. | Variance math proven |
| 6   | Notifications Lite | Makes v1 operationally usable without adding too much complexity. | Critical alerts delivered |
| 7   | Core reports | Needed for go-live trust, operator visibility, and user support. | Reports match source totals |

# 6\. Architecture decisions to lock before coding

1.  Every tenant-owned DocType must contain a mandatory \`chama\` link field.
2.  User identity and Chama membership identity remain separate objects.
3.  Contribution obligation and contribution payment remain separate objects.
4.  Loan lifecycle source of truth remains Frappe Lending; the Chama app wraps and extends it.
5.  Disbursement request and disbursement execution remain separate objects.
6.  Expected balance formula comes only from the canonical rule set and may not be redefined per report.
7.  No historical financial correction through silent edit; use reversals and adjustment records.
8.  All approval logic is server-side authoritative; UI only reflects state, never decides it.

# 7\. ERPNext mapping pack for v1

This section maps the v1 scope into concrete ERPNext/Frappe implementation artifacts. The purpose is to give Cursor and the engineering team a buildable translation layer from product intent to framework objects.

## 7.1 V1 artifact inventory summary

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **Module** | **Primary DocTypes / Objects** | **Workflow** | **Jobs** | **Key reports** |
| Foundation | Chama; Chama Settings; Chama Member; Chama Member Role Assignment; Chama Context Session | Chama lifecycle (light) | tenant_integrity_scan | Chama register |
| Contributions | Category; Cycle; Obligation; Payment; Allocation; Penalty Rule; Waiver | Waiver approval | cycle_generation; due_refresh; overdue_refresh | Contribution compliance; member statement section |
| Loans | Custom Loan fields; Chama Guarantor; Eligibility Snapshot | Loan approval | loan_overdue_refresh; default_check | Loan portfolio |
| Disbursements | Request; Execution; Approval Rule; Reversal | Disbursement approval | stale_execution_monitor | Disbursement register |
| Reconciliation Lite | Financial Period; Reconciliation Run; Source Balance; Issue | Adjustment optional light | variance_alert_scan | Reconciliation summary |
| Notifications Lite | Notification Event; Template; Queue; Inbox; Preference | Queue lifecycle | queue_process; retry_failed | Delivery register |
| Reports | Report Definition; Metric Definition (minimal) | n/a | metric_refresh optional light | Treasurer dashboard |

## Foundation / platform controls

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama | Custom DocType | Tenant master; Active/Inactive/Archived |
| Chama Settings | Custom DocType | Per-tenant defaults used by v1 modules |
| Chama Member | Custom DocType | Per-tenant member profile |
| Chama Member Role Assignment | Custom DocType | Time-bounded roles within a Chama |
| Chama Context Session | Custom DocType or audit log | Context-switch audit trail |

### Workflow / jobs / APIs

**Workflows:** Chama Lifecycle — Optional light workflow for Active / Inactive / Archived

**Scheduled jobs:** tenant_integrity_scan (Daily check for missing chama or broken tenant references)

**Primary APIs:** chama.platform.my_chamas; chama.platform.switch_context; chama.platform.create_chama

## Contributions

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama Contribution Category | Custom DocType | Recurring/ad hoc contribution types |
| Chama Contribution Cycle | Custom DocType | Generation batch per period |
| Chama Contribution Obligation | Custom DocType | Expected member dues |
| Chama Contribution Payment | Custom DocType | Recorded payment receipt |
| Contribution Payment Allocation | Child Table | Allocation rows per payment |
| Chama Penalty Rule | Custom DocType | Basic penalty logic |
| Chama Contribution Waiver | Custom DocType | Controlled waiver requests |

### Workflow / jobs / APIs

**Workflows:** Contribution Waiver Approval — Draft → Submitted → Approved / Rejected

**Scheduled jobs:** contribution_cycle_generation (Daily); contribution_due_status_refresh (Daily); contribution_overdue_refresh (Daily); contribution_penalty_apply (Daily)

**Primary APIs:** chama.contribution.generate_cycle; chama.contribution.submit_payment; chama.contribution.get_member_summary; chama.contribution.reverse_payment

## Loans

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama Guarantor | Custom DocType | Per-loan guarantor commitments |
| Loan Eligibility Snapshot | Custom DocType | Submission-time eligibility evidence |

### Required custom fields

|     |     |     |
| --- | --- | --- |
| **Field** | **Type** | **Purpose** |
| Loan.chama | Link(Chama) | Mandatory tenant anchor |
| Loan.member | Link(Chama Member) | Borrower |
| Loan.eligibility_snapshot | JSON/Long Text | Stored evaluation output |
| Loan.guarantor_status | Select | Pending / Complete |
| Loan.approval_required_level | Select | Treasurer / Chair / Auto |
| Loan.exception_flag | Check | Rule-break indicator |

### Workflow / jobs / APIs

**Workflows:** Loan Approval — Submitted → Under Review → Approved / Rejected

**Scheduled jobs:** loan_overdue_refresh (Daily); loan_default_check (Daily); loan_repayment_reminder_queue (Daily)

**Primary APIs:** chama.loan.apply; chama.loan.confirm_guarantor; chama.loan.loan_detail

## Disbursements

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama Disbursement Request | Custom DocType | Request basis and approval state |
| Chama Disbursement Execution | Custom DocType | Actual payout event |
| Chama Approval Rule | Custom DocType | Threshold routing |
| Chama Disbursement Reversal | Custom DocType | Reversal metadata |

### Workflow / jobs / APIs

**Workflows:** Disbursement Request Approval — Draft → Submitted → Under Review → Approved / Rejected

**Scheduled jobs:** pending_execution_monitor (Hourly); failed_disbursement_retry_review (Daily)

**Primary APIs:** chama.disbursement.submit_request; chama.disbursement.approve; chama.disbursement.execute; chama.disbursement.reverse

## Reconciliation Lite

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama Financial Period | Custom DocType | Open/close reporting periods |
| Chama Reconciliation Run | Custom DocType | Expected vs actual snapshot |
| Reconciliation Source Balance | Child Table | Source-level actual/expected rows |
| Chama Reconciliation Issue | Custom DocType | Basic discrepancy tracking |

### Workflow / jobs / APIs

**Workflows:** None beyond status validation in v1.

**Scheduled jobs:** reconciliation_variance_alert_check (Daily); period_close_precheck (Daily)

**Primary APIs:** chama.reconciliation.run; chama.reconciliation.status; chama.statement.get

## Notifications Lite

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama Notification Event | Custom DocType | Business event |
| Chama Notification Template | Custom DocType | APP/SMS templates |
| Chama Notification Queue | Custom DocType | Queued sends |
| Chama Notification Inbox | Custom DocType | In-app inbox items |
| Chama Notification Preference | Custom DocType | Per-user settings |

### Workflow / jobs / APIs

**Workflows:** None beyond status validation in v1.

**Scheduled jobs:** process_notification_queue (Every minute); retry_failed_notifications (Every 10 min); generate_due_reminders (Daily)

**Primary APIs:** chama.notification.inbox; chama.notification.mark_read; chama.notification.update_preferences

## Core reports & dashboards

### Primary DocTypes / framework objects

|     |     |     |
| --- | --- | --- |
| **Artifact** | **Type** | **Purpose** |
| Chama Report Definition | Custom DocType | Report catalog |
| Chama Metric Definition | Custom DocType | Canonical KPI registry |
| Chama Dashboard Layout | Custom DocType | Optional v1 dashboard layout |

### Workflow / jobs / APIs

**Workflows:** None beyond status validation in v1.

**Scheduled jobs:** metric_snapshot_refresh (Daily optional for heavy KPIs)

**Primary APIs:** chama.analytics.dashboard; chama.analytics.generate_report; chama.analytics.member_statement

# 8\. Release dependency cut-lines

The following dependencies must be respected in Cursor implementation order.

|     |     |     |
| --- | --- | --- |
| **Module** | **Hard dependency** | **Why dependency matters** |
| Contributions | Chama + Chama Member + permissions | Obligations and payments must be tenant-safe and member-scoped |
| Loans | Contributions + Frappe Lending + Member core | Eligibility and borrower identity depend on both |
| Disbursements | Loans + Member core | Loan-linked disbursements and member beneficiary checks |
| Reconciliation Lite | Contributions + Loans + Disbursements | Expected balance cannot be computed earlier |
| Notifications Lite | Core business events available | Must subscribe to real module events |
| Core reports | Underlying transactional modules stable | Reports must not be defined before source truth exists |

# 9\. Cursor execution guidance

Cursor should be used against small, reviewable engineering tasks. The project should not be handed to Cursor as one broad instruction.

## 9.1 Good Cursor ticket shapes

- Create the \`Chama Contribution Obligation\` DocType schema and server validations.
- Add custom fields to Lending Loan and patch form layout safely.
- Implement \`auto_allocate_payment(payment_name)\` with unit tests.
- Build \`loan_overdue_refresh\` scheduler job with idempotency guard.
- Create Query Report: Contribution Compliance.

## 9.2 Bad Cursor ticket shapes

- Build the contributions module.
- Implement the whole Chama system.
- Do all reports and dashboards.

## 9.3 Review discipline

- Review every migration and DocType diff before applying to staging.
- Review every workflow state change for invalid transitions.
- Run reconciliation sample data after every major financial module change.
- Never merge a Cursor-generated change that bypasses tenant scope checks.
- Keep formulas centralized; if Cursor duplicates them in multiple places, refactor immediately.

# 10\. Immediate next deliverables after this pack

- Create a task backlog from this v1 mapping pack.
- Create ERPNext/Frappe migration plan in build order.
- Implement foundation first and prove Chama isolation with test data.
- Implement contributions before loans.
- Bring reconciliation Lite in earlier than feels comfortable; it is the safety net.

# 11\. Acceptance gates for this v1 cut

|     |     |
| --- | --- |
| **Gate** | **Definition of done** |
| Tenant safety | No record from Chama A is visible or mutable in Chama B under normal user flows or API calls. |
| Contribution correctness | Obligation generation, payment allocation, overdue logic, and reversal behavior all match canonical formulas. |
| Loan integrity | Loan wrapper data matches Lending state; guarantor logic and eligibility snapshots are consistent. |
| Payout control | Disbursement execution cannot duplicate and always has an approved basis. |
| Balance trust | Expected balance from v1 transactions can be compared to actual balances and variance is explainable. |
| Operator usability | Treasurer can operate the Chama from core reports and notifications without needing backdoor DB inspection. |