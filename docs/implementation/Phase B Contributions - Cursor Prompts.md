**Phase B — Contributions: Cursor Prompts**

**Build order**

Use this order exactly:

1.  B-001 Contribution Category
2.  B-002 Contribution Cycle
3.  B-003 Contribution Obligation
4.  B-004 Contribution Payment
5.  B-005 Payment Allocation child table
6.  B-006 Allocation service
7.  B-007 Cycle generation job
8.  B-008 Due/overdue refresh job
9.  B-009 Payment submission API
10. B-010 Member contribution summary API
11. B-011 Basic reports

**B-001 — Create Chama Contribution Category**

Create a custom Frappe/ERPNext v16 DocType named "Chama Contribution Category".  
<br/>Context:  
\- This belongs to a multi-tenant Chama platform.  
\- Every business record must be tenant-scoped by \`chama\`.  
\- This DocType defines contribution categories such as Shares, Welfare, Emergency Fund, Levy, etc.  
<br/>Requirements:  
\- Module: Chama Contributions  
\- Is Submittable: No  
\- Naming: CCAT-.####  
\- Fields:  
1\. chama (Link, options Chama, reqd)  
2\. category_name (Data, reqd)  
3\. category_code (Data, reqd)  
4\. category_type (Select, reqd, options: Shares\\nWelfare\\nEmergency\\nInvestment\\nPenalty\\nLevy\\nJoining Fee\\nOther, default Shares)  
5\. amount_type (Select, reqd, options: Fixed\\nVariable, default Fixed)  
6\. default_amount (Currency)  
7\. frequency (Select, reqd, options: Weekly\\nMonthly\\nQuarterly\\nAnnual\\nAd Hoc, default Monthly)  
8\. mandatory (Check, default 1)  
9\. allow_partial_payment (Check, default 1)  
10\. allow_future_prepayment (Check, default 0)  
11\. grace_days (Int, default 0)  
12\. active (Check, default 1)  
13\. start_date (Date, reqd)  
14\. end_date (Date)  
<br/>Validation:  
\- category_name must be unique within a Chama  
\- category_code must be unique within a Chama  
\- if amount_type = Fixed, default_amount must be > 0  
\- end_date cannot be before start_date  
<br/>Output:  
\- Frappe DocType JSON  
\- Python controller with validate()  
\- production-style code only

**B-002 — Create Chama Contribution Cycle**

Create a custom Frappe/ERPNext v16 DocType named "Chama Contribution Cycle".  
<br/>Context:  
\- This represents a contribution generation period for a Chama.  
\- It will later be used to generate obligations.  
<br/>Requirements:  
\- Module: Chama Contributions  
\- Is Submittable: No  
\- Naming: field:cycle_name if possible, otherwise CYC-.####  
\- Fields:  
1\. chama (Link, options Chama, reqd)  
2\. cycle_name (Data, reqd)  
3\. period_start (Date, reqd)  
4\. period_end (Date, reqd)  
5\. frequency (Select, reqd, options: Weekly\\nMonthly\\nQuarterly\\nAnnual\\nAd Hoc)  
6\. status (Select, reqd, options: Draft\\nGenerated\\nClosed\\nCancelled, default Draft)  
7\. generated_on (Datetime, read_only)  
8\. generated_by (Link, options User)  
9\. notes (Small Text)  
<br/>Validation:  
\- period_end cannot be before period_start  
\- cycle_name should be unique within a Chama where practical  
<br/>Output:  
\- DocType JSON  
\- Python controller with validate()

**B-003 — Create Chama Contribution Obligation**

Create a custom Frappe/ERPNext v16 DocType named "Chama Contribution Obligation".  
<br/>Context:  
\- This is one of the most important transactional records.  
\- It represents what a member is expected to pay for a category in a cycle.  
\- It must be tenant-scoped and member-scoped.  
\- It must separate obligation from payment.  
<br/>Requirements:  
\- Module: Chama Contributions  
\- Is Submittable: No  
\- Naming: COB-.####  
\- Fields:  
1\. chama (Link, options Chama, reqd)  
2\. member (Link, options Chama Member, reqd)  
3\. cycle (Link, options Chama Contribution Cycle, reqd)  
4\. contribution_category (Link, options Chama Contribution Category, reqd)  
5\. amount_due (Currency, reqd)  
6\. amount_paid (Currency, default 0, read_only)  
7\. amount_waived (Currency, default 0, read_only)  
8\. amount_outstanding (Currency, read_only)  
9\. due_date (Date, reqd)  
10\. grace_end_date (Date, reqd)  
11\. status (Select, reqd, options: Pending\\nDue\\nPartially Paid\\nPaid\\nOverdue\\nWaived\\nCancelled, default Pending)  
12\. penalty_applied (Check, default 0)  
13\. source_type (Select, reqd, options: Scheduled\\nAd Hoc\\nAdjustment, default Scheduled)  
14\. notes (Small Text)  
<br/>Validation and behavior:  
\- member must belong to same Chama  
\- category must belong to same Chama  
\- cycle must belong to same Chama  
\- amount_due must be > 0  
\- amount_paid + amount_waived cannot exceed amount_due  
\- amount_outstanding must be computed as:  
amount_due - amount_paid - amount_waived  
\- amount_outstanding cannot be negative  
<br/>Also:  
\- compute amount_outstanding in validate()  
\- create a helper method to recompute status from amounts if useful  
<br/>Output:  
\- DocType JSON  
\- Python controller

**B-004 — Create Chama Contribution Payment**

Create a custom Frappe/ERPNext v16 DocType named "Chama Contribution Payment".  
<br/>Context:  
\- This represents one received contribution payment event.  
\- It must be separate from obligation and separate from allocation.  
\- It will later be linked to allocation child rows.  
\- It must support mobile money, bank, cash, and adjustments.  
<br/>Requirements:  
\- Module: Chama Contributions  
\- Is Submittable: No  
\- Naming: CPT-.####  
\- Fields:  
1\. chama (Link, options Chama, reqd)  
2\. member (Link, options Chama Member, reqd)  
3\. payment_date (Datetime, reqd)  
4\. amount_received (Currency, reqd)  
5\. payment_method (Select, reqd, options: Mobile Money\\nCash\\nBank\\nInternal Transfer\\nAdjustment, default Mobile Money)  
6\. payment_reference (Data)  
7\. source_channel (Select, reqd, options: Mobile\\nDesk\\nImport\\nAPI, default Desk)  
8\. status (Select, reqd, options: Recorded\\nAllocated\\nPartially Allocated\\nReversed\\nFlagged, default Recorded)  
9\. entered_by (Link, options User, reqd)  
10\. received_into_account (Data)  
11\. remarks (Small Text)  
12\. reversal_of (Link, options Chama Contribution Payment)  
13\. duplicate_flag (Check, default 0)  
<br/>Validation:  
\- member must belong to same Chama  
\- amount_received must be > 0  
\- if payment_method is not Cash and not Adjustment, payment_reference should be required or strongly validated  
\- detect obvious duplicate risk only as a flag/warning helper, not by blocking save automatically  
<br/>Output:  
\- DocType JSON  
\- Python controller  
\- include validate()

**B-005 — Create Contribution Payment Allocation child table**

Create a Frappe/ERPNext v16 child table DocType named "Contribution Payment Allocation".  
<br/>Context:  
\- Parent DocType: Chama Contribution Payment  
\- This child table allocates a single payment across one or more contribution obligations.  
<br/>Requirements:  
\- Module: Chama Contributions  
\- Is Child Table: Yes  
\- Fields:  
1\. obligation (Link, options Chama Contribution Obligation, reqd)  
2\. contribution_category (Link, options Chama Contribution Category)  
3\. allocated_amount (Currency, reqd)  
4\. allocation_order (Int, reqd)  
5\. allocation_type (Select, reqd, options: Due\\nOverdue\\nFuture\\nManual Reallocation, default Due)  
6\. notes (Small Text)  
<br/>Validation expectations:  
\- allocated_amount must be > 0  
<br/>Output:  
\- Child table DocType JSON  
\- minimal controller only if needed

**B-006 — Create contribution allocation service**

Create a production-grade Python service module for contribution payment allocation in a Frappe/ERPNext v16 Chama app.  
<br/>Suggested file:  
chama_contributions/services/allocation_engine.py  
<br/>Context:  
\- Payments must be allocated oldest-first by default.  
\- Allocation order:  
1\. Overdue obligations  
2\. Due obligations  
3\. Partially paid open obligations (oldest first)  
4\. Future obligations only if allowed  
\- Payment and obligation are separate records.  
\- Allocation must create child rows on Chama Contribution Payment.  
\- Obligation amounts must be updated transactionally.  
\- This must be tenant-safe.  
<br/>Implement:  
1\. get_open_obligations(chama, member, target_category=None, allow_future=False)  
2\. recompute_obligation_amounts_and_status(obligation_doc)  
3\. allocate_payment(payment_name, target_category=None, allow_future=False)  
4\. reverse_payment_allocations(payment_name)  
<br/>Rules:  
\- use Chama-scoped queries only  
\- never allow amount_paid + amount_waived > amount_due  
\- update payment status to Allocated or Partially Allocated  
\- if there is remaining unapplied amount, leave payment as Partially Allocated  
\- do not invent a credit wallet yet  
\- reverse_payment_allocations should subtract allocations from obligations and clear allocation rows safely  
<br/>Also:  
\- include clear docstrings  
\- raise clear frappe exceptions  
\- no pseudo-code

**B-007 — Create contribution cycle generation service and scheduler job**

Create a production-grade contribution cycle generation service for Frappe/ERPNext v16.  
<br/>Suggested files:  
\- chama_contributions/services/cycle_generation.py  
\- scheduler hook entry if appropriate  
<br/>Context:  
\- For each active Chama, active contribution categories should generate obligations for eligible members.  
\- Eligible members are normally Active members in that Chama.  
\- Each obligation must include:  
\- chama  
\- member  
\- cycle  
\- contribution_category  
\- amount_due  
\- due_date  
\- grace_end_date  
\- status Pending  
<br/>Implement:  
1\. get_active_categories(chama, target_date)  
2\. get_eligible_members(chama, target_date)  
3\. resolve_category_amount(category, member, target_date)  
4\. create_cycle(chama, period_start, period_end, frequency, generated_by=None)  
5\. generate_obligations_for_cycle(cycle_name)  
6\. generate_due_cycles_for_today()  
<br/>Rules:  
\- do not create duplicate cycles for same Chama + period + frequency  
\- do not create duplicate obligations for same member + category + cycle  
\- use grace_days from contribution category  
\- fixed amount uses default_amount  
\- variable amount can raise a clear not-implemented exception for now unless explicitly defined  
<br/>Also provide:  
\- a scheduler job function for daily generation  
\- code only, production style

**B-008 — Create due/overdue refresh and penalty skeleton job**

Create a production-grade scheduled service for refreshing contribution obligation states in Frappe/ERPNext v16.  
<br/>Suggested file:  
chama_contributions/services/obligation_status_jobs.py  
<br/>Implement:  
1\. refresh_due_statuses(today_date=None)  
2\. refresh_overdue_statuses(today_date=None)  
3\. apply_penalties_skeleton(today_date=None)  
<br/>Rules:  
\- Pending -> Due when today >= due_date and outstanding > 0  
\- Due or Partially Paid -> Overdue when today > grace_end_date and outstanding > 0  
\- Paid obligations must remain Paid  
\- Waived obligations must remain Waived  
\- Cancelled obligations must remain Cancelled  
\- apply_penalties_skeleton should detect overdue obligations where penalty_applied = 0 and log or mark candidates, but do not yet create full penalty obligations unless the rule is clearly defined  
<br/>Also:  
\- use tenant-safe queries  
\- batch updates safely  
\- include clear logging/comments  
\- no pseudo-code

**B-009 — Create contribution payment submission API**

Create a Frappe/ERPNext v16 whitelisted API endpoint for submitting a contribution payment.  
<br/>Suggested file:  
chama_contributions/api/payments.py  
<br/>Endpoint function:  
submit_payment  
<br/>Input:  
\- chama  
\- member  
\- amount_received  
\- payment_method  
\- payment_reference (optional depending on method)  
\- source_channel (optional)  
\- target_category (optional)  
<br/>Behavior:  
1\. validate logged-in user and Chama access  
2\. validate member belongs to Chama  
3\. create Chama Contribution Payment  
4\. call allocation_engine.allocate_payment()  
5\. return standard API success/error response  
<br/>Response shape must use shared response helpers:  
success:  
{  
"status": "success",  
"data": {  
"payment_id": "...",  
"payment_status": "...",  
"amount_received": ...  
},  
"errors": \[\]  
}  
<br/>Requirements:  
\- use service layer  
\- no direct business logic duplication in API  
\- clear validation errors  
\- production-grade code only

**B-010 — Create member contribution summary API**

Create a Frappe/ERPNext v16 whitelisted API endpoint to fetch a member contribution summary.  
<br/>Suggested file:  
chama_contributions/api/summary.py  
<br/>Endpoint function:  
get_member_contribution_summary  
<br/>Input:  
\- chama  
\- member  
\- cycle (optional)  
\- category (optional)  
<br/>Output must include:  
\- member  
\- total_due  
\- total_paid  
\- total_outstanding  
\- total_overdue  
\- obligations list with:  
\- obligation_id  
\- category  
\- amount_due  
\- amount_paid  
\- amount_outstanding  
\- due_date  
\- status  
<br/>Rules:  
\- member users should only access their own records unless officer role is allowed  
\- Chama context must be validated  
\- numbers must be derived from obligation records  
\- response must use standard response helper  
<br/>Production-grade code only.

**B-011 — Create baseline contribution reports**

Create baseline Frappe/ERPNext v16 reports for the Chama Contributions module.  
<br/>I want these reports:  
1\. Contribution Compliance Report  
2\. Overdue Contributions Report  
3\. Payment Register  
4\. Member Contribution Statement (report form, not API)  
<br/>For each report:  
\- propose whether Query Report or Script Report is more appropriate  
\- implement the report Python and JS/JSON where needed  
\- make all reports tenant-safe with mandatory Chama filter  
\- include useful filters such as:  
\- Chama  
\- Member  
\- Category  
\- Date range  
\- Status  
<br/>Definitions:  
\- Contribution Compliance Report columns:  
member, category, amount_due, amount_paid, outstanding, status, compliance_percent  
\- Overdue Contributions Report columns:  
member, category, due_date, grace_end_date, outstanding, overdue_days  
\- Payment Register columns:  
payment_id, member, payment_date, payment_method, payment_reference, amount_received, status  
\- Member Contribution Statement columns:  
date/cycle, category, amount_due, amount_paid, amount_waived, outstanding, status  
<br/>Code only, production-ready, Frappe v16 style.

**Recommended testing after each task**

**After B-001 to B-005**

Create:

- 1 Chama
- 3 members
- 2 categories
- 1 cycle
- 3 obligations
- 1 payment

Verify:

- all records have the right chama
- member/category/cycle cross-links are blocked if Chama mismatches

**After B-006**

Test:

- one payment covering one full obligation
- one partial payment
- one payment covering two obligations
- reverse payment

Verify:

- statuses update correctly
- no negative outstanding
- no over-allocation

**After B-007 and B-008**

Test:

- automatic cycle generation
- due transition
- overdue transition

Verify:

- no duplicate cycles
- no duplicate obligations
- state changes follow rules exactly

**After B-009 to B-011**

Test:

- member-facing payment submission
- officer payment submission
- summary numbers vs raw obligations
- report totals vs API totals

**Important warning for Phase B**

Do **not** let Cursor:

- merge payment and obligation into one model
- put allocation logic inside the API
- skip Chama validation
- invent a wallet/credit subsystem yet
- create penalty logic beyond the approved skeleton

Keep Phase B tight.