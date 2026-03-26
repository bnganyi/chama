**📘 V1 IMPLEMENTATION BACKLOG (CURSOR-READY)**

**1\. BACKLOG STRUCTURE (IMPORTANT)**

Each task follows this format:

- **ID**
- **Module**
- **Task Type** (DocType / API / Workflow / Job / UI / Integration)
- **Description**
- **Inputs**
- **Output**
- **Dependencies**

Cursor works best when you feed it **one task at a time** from this.

**🧱 PHASE A — FOUNDATION (DO FIRST, NO SHORTCUTS)**

**A-001 — Create Chama DocType**

- **Type:** DocType
- **Description:** Core tenant entity
- **Fields:**
    - name (auto)
    - chama_name
    - currency
    - timezone
    - status (Active / Archived)
- **Output:** Chama DocType
- **Dependency:** none

👉 Cursor prompt:

Create Frappe DocType "Chama" with fields...

**A-002 — Create Chama Settings DocType**

- **Type:** DocType
- **Fields:**
    - chama (Link)
    - contribution_policy_json
    - loan_policy_json
    - notification_preferences_json
- **Dependency:** A-001

**A-003 — Create Chama Member DocType**

- **Type:** DocType
- **Fields:**
    - member_id
    - user (Link User)
    - chama (Link Chama)
    - status
    - join_date
- **Dependency:** A-001

**A-004 — Chama Role Assignment**

- **Type:** DocType
- **Fields:**
    - member
    - chama
    - role (Treasurer / Chair / etc)
- **Dependency:** A-003

**A-005 — Enforce Tenant Filtering Hook**

- **Type:** Server Hook
- **Description:** Ensure all queries filter by chama
- **Output:** global query guard
- **Dependency:** A-001

👉 This is critical. Don’t move forward without it.

**A-006 — Context Switching API**

- **Type:** API
- **Endpoint:** chama.context.switch
- **Output:** stores active chama in session
- **Dependency:** A-003

**A-007 — Permission Enforcement Layer**

- **Type:** Logic
- **Description:** role + chama-based access checks
- **Dependency:** A-004

**💰 PHASE B — CONTRIBUTIONS (BUILD FIRST BUSINESS LOGIC)**

**B-001 — Contribution Category**

- name
- amount_type (fixed/variable)
- default_amount

**B-002 — Contribution Cycle**

- period
- category
- status

**B-003 — Contribution Obligation**

- member
- amount_due
- due_date
- outstanding

**B-004 — Contribution Payment**

- member
- amount
- payment_date

**B-005 — Payment Allocation Table**

- obligation
- allocated_amount

**B-006 — Allocation Engine (CORE LOGIC)**

- **Type:** Service
- Implements:

allocate_payment(payment):  
apply oldest-first

**B-007 — Obligation Generation Job**

- **Type:** Scheduler
- generates obligations per cycle

**B-008 — Overdue Detection Job**

- marks overdue obligations

**B-009 — Contribution API**

- submit payment
- get obligations
- get member summary

**B-010 — Contribution Reports**

- compliance report
- member contribution statement

**🏦 PHASE C — LOANS (ERPNext INTEGRATION)**

**C-001 — Extend Loan DocType (Lending)**

- add:
    - chama
    - member
    - guarantor_required_amount

**C-002 — Create Guarantor DocType**

- loan
- member
- guaranteed_amount

**C-003 — Loan Eligibility Service**

- computes max eligible loan

**C-004 — Loan Application API**

- chama.loan.apply

**C-005 — Loan Approval Workflow**

- Draft → Submitted → Approved → Rejected

**C-006 — Loan Sync Handler**

- ensures:
    - disbursement reflects in system
    - repayment reflects in contributions/analytics

**C-007 — Loan Dashboard View**

- borrower view
- treasurer view

**💸 PHASE D — DISBURSEMENTS**

**D-001 — Disbursement Request**

- beneficiary
- amount
- status

**D-002 — Disbursement Execution**

- request
- executed_amount
- execution_date

**D-003 — Approval Workflow**

- Submitted → Review → Approved → Rejected

**D-004 — Execution Service**

- validates:
    - approval
    - funds
- records execution

**D-005 — Reversal Service**

- creates compensating record

**D-006 — Disbursement API**

- submit request
- approve
- execute

**D-007 — Disbursement Report**

**📊 PHASE E — RECONCILIATION (DO EARLY, NOT LATE)**

**E-001 — Financial Period**

- start_date
- end_date
- status

**E-002 — Reconciliation Run**

- expected_balance
- actual_balance
- variance

**E-003 — Expected Balance Engine**

Implements:

expected =  
inflows - outflows + adjustments

**E-004 — Reconciliation API**

**E-005 — Issue Logging**

- variance issues

**E-006 — Reconciliation Report**

**🔔 PHASE F — NOTIFICATIONS (LIGHT VERSION)**

**F-001 — Notification Event**

**F-002 — Notification Queue**

**F-003 — Inbox**

**F-004 — Queue Processor Job**

- runs every minute

**F-005 — Event Triggers**

- contribution due
- loan approved
- disbursement executed

**📈 PHASE G — REPORTS & DASHBOARD**

**G-001 — Member Statement API**

**G-002 — Contribution Report**

**G-003 — Loan Portfolio**

**G-004 — Disbursement Register**

**G-005 — Reconciliation Summary**

**G-006 — Treasurer Dashboard**

**🔗 CRITICAL DEPENDENCY ORDER**

DO NOT BREAK THIS:

1.  Foundation
2.  Contributions
3.  Loans
4.  Disbursements
5.  Reconciliation
6.  Notifications
7.  Reports

**⚠️ WHAT TO BUILD FIRST (DAY 1–3)**

If you want the fastest meaningful start:

1.  Chama + Member + Context
2.  Contribution Obligation + Payment
3.  Allocation Engine
4.  Contribution Report

That alone already gives you:  
👉 a working financial core

**🧠 HOW TO USE THIS WITH CURSOR**

For each task:

**Step 1**

Paste task into Cursor:

“Implement B-006 Allocation Engine…”

**Step 2**

Review output manually

**Step 3**

Test immediately

**Step 4**

Move to next task

**🔥 STRATEGIC ADVICE (IMPORTANT)**

Do NOT:

- generate multiple modules at once
- trust generated workflows blindly
- skip reconciliation early
- delay testing until “later”

Do:

- test each module before moving on
- validate numbers manually
- enforce tenant isolation early
- keep PRD open while coding