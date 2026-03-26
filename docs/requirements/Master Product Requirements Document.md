# Master Product Requirements Document

# SECTION 1: SYSTEM OVERVIEW

**1.1 System Identity**

**System Name:** Chama Financial Operating Platform  
**Architecture Base:** ERPNext + Frappe Framework  
**Loan Engine:** Frappe Lending

**1.2 System Purpose**

This system provides:

- End-to-end financial management for Chamas
- Governance and decision-making workflows
- Multi-tenant (multi-Chama) architecture
- Member lifecycle and accountability
- Investment and wealth tracking

**1.3 Architecture Philosophy (NON-NEGOTIABLE)**

**1.3.1 Reuse-First Principle**

The system MUST:

- Use ERPNext native features wherever possible
- Extend via custom app only when necessary
- Avoid duplicating core ERPNext functionality

**1.3.2 Layered Architecture**

\[ Mobile App \]  
↓  
\[ API Layer (Frappe REST + Custom Methods) \]  
↓  
\[ Business Logic (Custom App + ERPNext + Lending) \]  
↓  
\[ Data Layer (DocTypes) \]

**1.3.3 System of Record Rules**

| **Domain** | **System Owner** |
| --- | --- |
| Loans | Frappe Lending |
| Accounting | ERPNext |
| Members | Custom (extended ERPNext) |
| Contributions | Custom |
| Governance | Custom |

**1.4 Multi-Tenant Architecture (CORE RULE)**

**Rule:**

EVERY record MUST have a chama_id

**Implementation:**

**Field (MANDATORY on all DocTypes):**

fieldname: chama  
type: Link (Chama)  
reqd: 1

**Enforcement:**

- Query filters
- Permission rules
- API filtering
- UI context filtering

**1.5 User & Identity Model**

**1.5.1 User vs Member**

| **Concept** | **Description** |
| --- | --- |
| User | Authentication entity (ERPNext User) |
| Member | Chama-specific profile |

**1.5.2 Relationship**

User (1) → (Many) Member Records (per Chama)

**1.5.3 Member DocType (Core)**

**Fields:**

| **Field** | **Type** | **Required** |
| --- | --- | --- |
| member_id | Data (Auto) | Yes |
| user | Link (User) | Yes |
| chama | Link (Chama) | Yes |
| full_name | Data | Yes |
| phone | Data | Yes |
| national_id | Data | Yes |
| status | Select | Yes |
| join_date | Date | Yes |

**1.6 Permission Architecture**

**1.6.1 Role Model**

ERPNext Roles used:

- Member
- Treasurer
- Chairperson
- Secretary
- Auditor
- System Admin

**1.6.2 Chama-Scoped Permissions**

All permissions must include:

condition: doc.chama == user.current_chama

**1.6.3 Field-Level Permissions (Example)**

| **Field** | **Role** | **Access** |
| --- | --- | --- |
| loan_amount | Member | Read |
| loan_amount | Treasurer | Write |
| approval_status | Chair | Write |

**1.7 Audit & Compliance Model (MANDATORY)**

**1.7.1 Audit Log Requirements**

Every critical action must log:

| **Field** | **Description** |
| --- | --- |
| user | who performed |
| timestamp | when |
| action | what |
| before_value | previous |
| after_value | new |

**1.7.2 No-Delete Rule**

Financial and governance records MUST NEVER be deleted

Instead:

- Cancel
- Reverse
- Adjust

**1.8 Data Integrity Rules**

**1.8.1 Financial Integrity**

- Every transaction must be traceable
- No orphan records
- No silent corrections

**1.8.2 Referential Integrity**

- All links must be valid
- No broken references

**1.9 API Architecture**

**1.9.1 Standard APIs**

Use:

- /api/resource/{doctype}
- /api/method/{custom_method}

**1.9.2 Authentication**

- Token-based (for mobile)
- Session-based (for web)

**1.9.3 Response Standard**

{  
"status": "success",  
"data": {},  
"errors": \[\]  
}

**1.10 Notification Architecture**

**Components:**

- Notification Event
- Notification Template
- Delivery Channel
- Queue Processor

**Channels:**

- In-App
- SMS
- Email (optional)

**1.11 Scheduler & Background Jobs**

**Required Jobs:**

| **Job** | **Frequency** |
| --- | --- |
| Contribution cycle | Daily |
| Loan overdue check | Daily |
| Notification dispatch | Real-time |
| Reconciliation alerts | Daily |

**1.12 Performance Requirements**

- All dashboards < 2 seconds load
- API response < 500ms (excluding heavy reports)
- Background jobs async

**1.13 Security Requirements**

**MUST:**

- Enforce Chama isolation
- Prevent privilege escalation
- Validate all inputs
- Protect financial endpoints

# SECTION 2: GLOBAL STANDARDS

**2.1 Naming Conventions**

**DocTypes**

| **Type** | **Format** |
| --- | --- |
| Core | Chama Member |
| Transactional | Chama Contribution |
| Linking | Chama Guarantor |

**Fields**

| **Type** | **Format** |
| --- | --- |
| ID  | snake_case |
| Label | Title Case |

**2.2 ID & Numbering Standards**

**Format:**

| **Entity** | **Example** |
| --- | --- |
| Loan | LN-0001 |
| Contribution | CN-0001 |
| Disbursement | DB-0001 |
| Member | MB-0001 |

**2.3 Currency Handling**

- Base currency: configurable per Chama
- Precision: 2 decimal places
- No mixed currency within Chama (v1)

**2.4 Date & Time**

- Store in UTC
- Display in user locale
- All deadlines timezone-aware

**2.5 Status Fields (STANDARDIZED)**

All status fields must use:

| **Value** | **Meaning** |
| --- | --- |
| Draft | Not submitted |
| Submitted | Awaiting action |
| Approved | Accepted |
| Rejected | Declined |
| Cancelled | Stopped |

**2.6 Error Handling Standard**

**Format:**

{  
"error_code": "LOAN_001",  
"message": "Insufficient guarantors",  
"details": {}  
}

**2.7 Logging Standard**

All logs must include:

- module
- chama
- user
- action
- timestamp

**2.8 Data Validation Rules**

- Required fields enforced at DocType level
- Server-side validation mandatory
- Client validation is supplementary only

**2.9 Configuration Management**

All configurable items must be stored in:

- Chama Settings DocType

Includes:

- contribution rules
- loan limits
- penalty rules
- notification preferences

**2.10 Extensibility Rules**

Customizations must:

- use hooks
- avoid core overrides
- be exportable

# SECTION 3: SHARED COMPONENTS

**3.1 MEMBER CORE MODEL (FOUNDATIONAL)**

This is the **single most important shared object**.

**3.1.1 DocType: Chama Member**

**ERPNext Type:**

- DocType (custom)
- Is Submittable: No
- Is Child Table: No

**3.1.2 Fields (FULL DICTIONARY)**

| **Field Name** | **Label** | **Type** | **Req** | **Default** | **Validation** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| name | Member ID | Data (Auto) | Yes | Auto | Unique | Format: MB-XXXX |
| user | User | Link(User) | Yes | —   | Must exist | One user can have many members |
| chama | Chama | Link(Chama) | Yes | —   | Required | Multi-tenant anchor |
| full_name | Full Name | Data | Yes | —   | Not empty |     |
| phone | Phone | Data | Yes | —   | Regex (phone) | Unique per Chama |
| national_id | National ID | Data | Yes | —   | Unique per Chama |     |
| email | Email | Data | No  | —   | Email format |     |
| status | Status | Select | Yes | Pending | Enum | See states below |
| join_date | Join Date | Date | Yes | Today | —   |     |
| exit_date | Exit Date | Date | No  | —   | Must be > join_date |     |
| role_profile | Role Profile | Link(Role Profile) | Yes | Member | —   | ERPNext Role Profile |
| is_active | Is Active | Check | Yes | 1   | —   | Derived from status |

**3.1.3 Status Enum**

Pending  
Active  
Suspended  
Dormant  
Exited

**3.1.4 State Transition Table (FORMAL)**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Pending | Active | Approval | Chair/Admin | Valid data | Create obligations |
| Active | Suspended | Rule breach | System/Admin | Non-payment | Restrict access |
| Suspended | Active | Resolution | Chair | Cleared dues | Restore access |
| Active | Exited | Exit process | Member/Admin | Settlement done | Lock records |

**3.1.5 Hooks**

validate():  
enforce_unique_phone_per_chama()  
<br/>on_update():  
update_user_permissions()

**3.2 CHAMA CORE MODEL**

**3.2.1 DocType: Chama**

**Fields**

| **Field** | **Type** | **Required** |
| --- | --- | --- |
| name | Data | Yes |
| code | Data (Unique) | Yes |
| status | Select | Yes |
| base_currency | Link(Currency) | Yes |
| created_on | Datetime | Yes |

**Status**

Active  
Inactive  
Archived

**3.3 PERMISSION ENGINE (STRICT)**

**3.3.1 Rule (MANDATORY)**

doc.chama == frappe.session.user_chama

**3.3.2 Implementation**

**Via User Permissions:**

- Link User → Chama
- Restrict DocTypes by Chama

**3.3.3 Permission Matrix (ENGINE LEVEL)**

| **Role** | **Scope** | **Restrictions** |
| --- | --- | --- |
| Member | Own records | No cross-member |
| Treasurer | Chama-wide | Financial only |
| Chair | Chama-wide | Approval rights |
| Admin | Global | Config only |

**3.4 NOTIFICATION ENGINE (FULL)**

**3.4.1 DocType: Chama Notification**

**Fields**

| **Field** | **Type** |
| --- | --- |
| recipient | Link(User) |
| chama | Link(Chama) |
| event_type | Data |
| message | Text |
| status | Select |
| channel | Select |
| created_at | Datetime |
| read_at | Datetime |

**Status**

Pending  
Sent  
Failed  
Read

**3.4.2 Template DocType**

Notification Template

| **Field** | **Type** |
| --- | --- |
| name | Data |
| event_type | Data |
| template | Text (Jinja) |

**3.4.3 Delivery Flow**

Event → Template → Queue → Channel → Status Update

**3.4.4 Background Job**

def process_notifications():  
pending = get_pending_notifications()  
for n in pending:  
send(n)  
update_status(n)

**3.5 AUDIT LOG SYSTEM**

**3.5.1 DocType: Chama Audit Log**

**Fields**

| **Field** | **Type** |
| --- | --- |
| user | Link(User) |
| chama | Link(Chama) |
| doctype | Data |
| docname | Data |
| action | Data |
| before | JSON |
| after | JSON |
| timestamp | Datetime |

**3.5.2 Trigger Points**

- Before update
- After update
- On submit
- On cancel

**3.5.3 Hook Example**

def on_update(doc):  
log_change(doc)

**3.6 CONFIGURATION ENGINE**

**DocType: Chama Settings**

**Fields**

| **Field** | **Type** |
| --- | --- |
| chama | Link |
| contribution_rules | JSON |
| loan_rules | JSON |
| penalty_rules | JSON |
| notification_settings | JSON |

**3.7 SHARED UTILITIES**

**3.7.1 Currency Utility**

def format_currency(amount):  
return round(amount, 2)

**3.7.2 Date Utility**

- Always UTC in DB
- Convert on display

**3.7.3 ID Generator**

MB-0001  
LN-0001  
CN-0001

**3.8 CROSS-MODULE DEPENDENCIES (IMPORTANT)**

**3.8.1 Eligibility Logic**

Loan Eligibility =  
f(contributions, tenure, outstanding_loans)

**3.8.2 Exit Settlement**

Final Balance =  
Contributions + Shares + Investments  
\- Loans - Penalties

**3.8.3 Budget Enforcement**

Disbursement Allowed =  
actual_spent < budget_limit

**⚠️ CRITICAL RULES (SYSTEM-WIDE)**

✔ Every record MUST have chama  
✔ No delete for financial data  
✔ All actions logged  
✔ Permissions strictly enforced  
✔ Background jobs must be idempotent

# SECTION 4: MODULE IMPLEMENTATION

## MODULE 4.1 — LOANS

**4.1.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| **Loan Core** | **Frappe Lending** |
| **Eligibility** | **Custom App** |
| **Guarantors** | **Custom** |
| **Approval** | **ERPNext Workflow** |
| **UI** | **Desk + Mobile** |

**4.1.2 DATA MODEL (FULL)**

**A. Core Loan (Frappe Lending)**

**We DO NOT redefine it. We extend it.**

**Extended Fields (Custom Fields on Loan)**

| **Field Name** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- |
| **chama** | **Link(Chama)** | **Yes** | **Tenant anchor** |
| **member** | **Link(Chama Member)** | **Yes** | **Borrower** |
| **eligibility_snapshot** | **JSON** | **Yes** | **Stored at submission** |
| **guarantor_status** | **Select** | **Yes** | **Pending/Complete** |
| **approval_required_level** | **Select** | **Yes** | **Auto/Treasurer/Chair** |
| **exception_flag** | **Check** | **Yes** | **If rule broken** |

**B. DocType: Chama Guarantor**

**Fields (FULL)**

| **Field Name** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- |
| **name** | **Data** | **Yes** | **ID** |
| **loan** | **Link(Loan)** | **Yes** | **Parent loan** |
| **chama** | **Link(Chama)** | **Yes** |     |
| **borrower** | **Link(Member)** | **Yes** |     |
| **guarantor** | **Link(Member)** | **Yes** |     |
| **requested_amount** | **Currency** | **Yes** |     |
| **confirmed_amount** | **Currency** | **No** |     |
| **status** | **Select** | **Yes** | **Pending/Confirmed/Rejected** |
| **exposure_after** | **Currency** | **Yes** |     |
| **confirmed_at** | **Datetime** | **No** |     |

**Constraints**

**guarantor != borrower  
sum(confirmed_amount) >= loan.amount**

**C. DocType: Loan Eligibility Snapshot**

**Fields**

| **Field** | **Type** |
| --- | --- |
| **loan** | **Link** |
| **chama** | **Link** |
| **member** | **Link** |
| **shares_balance** | **Currency** |
| **contribution_score** | **Float** |
| **max_eligible_amount** | **Currency** |
| **outstanding_loans** | **Currency** |
| **rule_flags** | **JSON** |

**4.1.3 STATE MACHINES (FORMAL)**

**A. Workflow State**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| **Draft** | **Submitted** | **Submit** | **Member** | **Valid input** | **Create guarantors** |
| **Submitted** | **Under Review** | **Auto** | **System** | **—** | **Notify treasurer** |
| **Under Review** | **Approved** | **Approve** | **Treasurer/Chair** | **Guarantors OK** | **Enable disbursement** |
| **Under Review** | **Rejected** | **Reject** | **Treasurer/Chair** | **—** | **Notify member** |

**B. Operational State (Loan)**

| **From** | **To** | **Trigger** | **Conditions** |
| --- | --- | --- | --- |
| **Approved** | **Disbursed** | **Lending action** | **Funds available** |
| **Disbursed** | **Active** | **Auto** | **—** |
| **Active** | **Overdue** | **Scheduler** | **Missed payment** |
| **Overdue** | **Defaulted** | **Threshold** | **Days exceeded** |
| **Active** | **Closed** | **Full repayment** | **Balance = 0** |

**4.1.4 ACTION DEFINITIONS**

**A. Submit Loan**

**Input**

**{  
"member_id": "MB-0001",  
"loan_product": "LP-001",  
"amount": 10000,  
"tenor": 6  
}**

**Process**

1.  **Fetch eligibility**
2.  **Validate:**
    - **amount <= max**
    - **member active**
3.  **Create Loan (Lending)**
4.  **Create Guarantor records**
5.  **Save snapshot**

**Output**

**{  
"loan_id": "LN-0001",  
"status": "Submitted"  
}**

**Errors**

| **Code** | **Message** |
| --- | --- |
| **LN001** | **Amount exceeds eligibility** |
| **LN002** | **Member inactive** |
| **LN003** | **Missing guarantors** |

**B. Confirm Guarantor**

**Input**

**{  
"loan_id": "LN-0001",  
"guarantor_id": "MB-002",  
"action": "accept"  
}**

**Process**

- **validate capacity**
- **update status**
- **recalc totals**

**4.1.5 ELIGIBILITY ENGINE**

**Formula**

**max_loan =  
min(  
shares \* multiplier,  
contribution_score \* factor  
)**

**Implementation**

**def calculate_eligibility(member):  
shares = get_shares(member)  
score = get_contribution_score(member)  
return min(shares \* 3, score \* 10000)**

**4.1.6 ERPNext WORKFLOW CONFIG**

**Workflow Name: Loan Approval**

| **State** | **Role** | **Action** |
| --- | --- | --- |
| **Submitted** | **System** | **Auto** |
| **Under Review** | **Treasurer** | **Approve/Reject** |
| **Approved** | **Chair (if needed)** | **Confirm** |

**4.1.7 PERMISSIONS (FIELD LEVEL)**

| **Field** | **Member** | **Treasurer** | **Chair** |
| --- | --- | --- | --- |
| **amount** | **R** | **R/W** | **R** |
| **status** | **R** | **R/W** | **R/W** |
| **approval** | **—** | **—** | **W** |

**4.1.8 API ENDPOINTS (FULL)**

**Apply Loan**

**POST /api/method/chama.loan.apply**

**Get Loans**

**GET /api/resource/Loan?filters=\[\["chama","=","CH-001"\]\]**

**4.1.9 SCHEDULERS**

| **Job** | **Frequency** |
| --- | --- |
| **Overdue check** | **Daily** |
| **Default trigger** | **Daily** |

**4.1.10 EDGE CASE HANDLING**

| **Case** | **Behavior** |
| --- | --- |
| **Guarantor rejects** | **Reset to Pending** |
| **Partial repayment** | **Keep overdue** |
| **Duplicate payment** | **Flag** |

**4.1.11 ERPNext CUSTOMIZATION SUMMARY**

| **Type** | **Item** |
| --- | --- |
| **Custom Fields** | **Loan** |
| **Custom DocTypes** | **Guarantor, Snapshot** |
| **Workflow** | **Loan Approval** |
| **Server Scripts** | **Eligibility** |

**⚠️ CRITICAL IMPLEMENTATION RULES**

**✔ Never override Lending core logic  
✔ Always extend via custom fields  
✔ Maintain audit trail  
✔ All loan records MUST include chama**

## MODULE 4.2 — CONTRIBUTIONS

**4.2.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Member, Chama, permissions | Custom app + ERPNext |
| Contribution rules/configuration | Custom |
| Contribution obligations | Custom |
| Contribution receipts/payments | Custom, optionally linked to ERPNext accounting later |
| Notifications | Shared notification engine |
| Reporting | ERPNext reports + custom logic |

**4.2.2 MODULE PURPOSE**

The Contributions module shall manage:

- scheduled and ad hoc member obligations
- multiple contribution categories
- payment capture and allocation
- overdue detection
- penalties
- waivers
- member contribution visibility
- contribution-derived analytics and downstream dependencies

This module must explicitly separate:

1.  **Contribution Obligation**  
    what the member is expected to pay
2.  **Contribution Payment**  
    what was actually received

That separation is mandatory.

**4.2.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall be built primarily using custom DocTypes because ERPNext does not natively provide a Chama obligation engine in the exact form required here.

Reuse from ERPNext/Frappe:

- users and roles
- permissions
- reports
- scheduler/background jobs
- notifications
- file attachments
- list/form/report UI
- workflow if needed for waivers or exceptional actions

Custom Chama layer:

- contribution categories
- recurring obligation generation
- payment allocation logic
- status engine
- penalty engine
- carry-forward / credit logic
- Chama-specific member statements

**4.2.4 DATA MODEL (FULL)**

**A. DocType: Chama Contribution Category**

**Purpose**

Defines the kinds of contributions a Chama uses.

**DocType Type**

- Custom DocType
- Is Submittable: No
- Is Child Table: No

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Default** | **Validation** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| name | Category ID | Data (Auto) | Yes | Auto | Unique | Example: CCAT-0001 |
| chama | Chama | Link(Chama) | Yes | —   | Required | Tenant anchor |
| category_name | Category Name | Data | Yes | —   | Unique within Chama | Example: Shares |
| category_code | Category Code | Data | Yes | —   | Unique within Chama | Example: SHR |
| category_type | Category Type | Select | Yes | Shares | Enum | Shares, Welfare, Emergency, Investment, Penalty, Levy, Joining Fee, Other |
| amount_type | Amount Type | Select | Yes | Fixed | Fixed / Variable |     |
| default_amount | Default Amount | Currency | No  | 0   | \>= 0 | Required if fixed |
| frequency | Frequency | Select | Yes | Monthly | Weekly, Monthly, Quarterly, Annual, Ad Hoc |     |
| mandatory | Mandatory | Check | Yes | 1   | —   |     |
| allow_partial_payment | Allow Partial Payment | Check | Yes | 1   | —   |     |
| allow_future_prepayment | Allow Future Prepayment | Check | Yes | 0   | —   |     |
| grace_days | Grace Days | Int | Yes | 0   | \>= 0 |     |
| penalty_rule | Penalty Rule | Link(Chama Penalty Rule) | No  | —   | Must match chama |     |
| active | Active | Check | Yes | 1   | —   |     |
| start_date | Start Date | Date | Yes | Today | —   |     |
| end_date | End Date | Date | No  | —   | end >= start |     |

**Constraints**

validate():  
enforce_unique(\["chama", "category_name"\])  
enforce_unique(\["chama", "category_code"\])  
if amount_type == "Fixed" and default_amount <= 0:  
frappe.throw("Default Amount is required for fixed categories")

**B. DocType: Chama Contribution Cycle**

**Purpose**

Represents a generation batch / period for obligations.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Cycle ID | Data (Auto) | Yes | Example CY-2026-03 |
| chama | Chama | Link(Chama) | Yes |     |
| cycle_name | Cycle Name | Data | Yes | Human-readable label |
| period_start | Period Start | Date | Yes |     |
| period_end | Period End | Date | Yes |     |
| frequency | Frequency | Select | Yes | Weekly / Monthly / etc |
| status | Status | Select | Yes | Draft / Generated / Closed / Cancelled |
| generated_on | Generated On | Datetime | No  |     |
| generated_by | Generated By | Link(User) | No  |     |
| notes | Notes | Small Text | No  |     |

**Constraints**

validate():  
if period_end < period_start:  
frappe.throw("Period End cannot be before Period Start")

**C. DocType: Chama Contribution Obligation**

**Purpose**

Represents one member’s expected contribution for one category in one cycle.

**This is the most important transactional record in the Contributions module.**

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Default** | **Validation** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| name | Obligation ID | Data (Auto) | Yes | Auto | Unique | Example: COB-0001 |
| chama | Chama | Link(Chama) | Yes | —   | Required |     |
| member | Member | Link(Chama Member) | Yes | —   | Must belong to same Chama |     |
| cycle | Contribution Cycle | Link(Chama Contribution Cycle) | Yes | —   | Required |     |
| contribution_category | Contribution Category | Link(Chama Contribution Category) | Yes | —   | Same Chama |     |
| amount_due | Amount Due | Currency | Yes | —   | \> 0 |     |
| amount_paid | Amount Paid | Currency | Yes | 0   | \>= 0 | Aggregate of allocations |
| amount_outstanding | Amount Outstanding | Currency | Yes | Computed | \>= 0 | amount_due - paid - waived |
| amount_waived | Amount Waived | Currency | Yes | 0   | \>= 0 |     |
| due_date | Due Date | Date | Yes | —   | Required |     |
| grace_end_date | Grace End Date | Date | Yes | —   | due + grace |     |
| status | Status | Select | Yes | Pending | Pending / Due / Partially Paid / Paid / Overdue / Waived / Cancelled |     |
| penalty_applied | Check | Yes | 0   | —   |     |     |
| parent_obligation | Parent Obligation | Link(Chama Contribution Obligation) | No  | —   | For split/restructured cases |     |
| source_type | Source Type | Select | Yes | Scheduled | Scheduled / Ad Hoc / Adjustment |     |
| notes | Notes | Small Text | No  | —   |     |     |

**Computed Rules**

amount_outstanding = amount_due - amount_paid - amount_waived

**Constraints**

validate():  
ensure_member_matches_chama()  
ensure_category_matches_chama()  
if amount_paid + amount_waived > amount_due:  
frappe.throw("Paid + Waived cannot exceed Amount Due")

**D. DocType: Chama Contribution Payment**

**Purpose**

Represents one received payment event, regardless of how it is allocated.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Default** | **Validation** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| name | Payment ID | Data (Auto) | Yes | Auto | Unique | Example: CPT-0001 |
| chama | Chama | Link(Chama) | Yes | —   | Required |     |
| member | Member | Link(Chama Member) | Yes | —   | Must belong to same Chama |     |
| payment_date | Payment Date | Datetime | Yes | Now | —   |     |
| amount_received | Amount Received | Currency | Yes | —   | \> 0 |     |
| payment_method | Payment Method | Select | Yes | Mobile Money | Mobile Money / Cash / Bank / Internal Transfer / Adjustment |     |
| payment_reference | Payment Reference | Data | No  | —   | Unique where appropriate | M-Pesa code / bank ref |
| source_channel | Source Channel | Select | Yes | Mobile | Mobile / Desk / Import / API |     |
| status | Status | Select | Yes | Recorded | Recorded / Allocated / Partially Allocated / Reversed / Flagged |     |
| entered_by | Entered By | Link(User) | Yes | Session User | —   |     |
| received_into_account | Received Into Account | Data | No  | —   | wallet/bank/cashbox reference |     |
| remarks | Remarks | Small Text | No  | —   |     |     |
| reversal_of | Reversal Of | Link(Chama Contribution Payment) | No  | —   | For reversals |     |
| duplicate_flag | Duplicate Flag | Check | Yes | 0   | —   |     |

**Constraints**

validate():  
if payment_method != "Cash" and not payment_reference and source_channel != "Adjustment":  
warn_or_require_reference()

**E. Child Table: Contribution Payment Allocation**

**Purpose**

Allocates a payment across one or more obligations.

**Parent**

Chama Contribution Payment

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| obligation | Obligation | Link(Chama Contribution Obligation) | Yes |     |
| contribution_category | Category | Link(Chama Contribution Category) | Yes | Convenience |
| allocated_amount | Allocated Amount | Currency | Yes | \> 0 |
| allocation_order | Allocation Order | Int | Yes | 1..n |
| allocation_type | Allocation Type | Select | Yes | Due / Overdue / Future / Manual Reallocation |
| notes | Notes | Small Text | No  |     |

**Constraints**

sum(allocation.allocated_amount) <= payment.amount_received

**F. DocType: Chama Penalty Rule**

**Purpose**

Reusable penalty settings for overdue obligations.

**Fields**

| **Field** | **Type** | **Req** | **Notes** |
| --- | --- | --- | --- |
| name | Data | Yes |     |
| chama | Link(Chama) | Yes |     |
| rule_name | Data | Yes |     |
| penalty_type | Select | Yes | Fixed / Percentage |
| penalty_value | Currency/Percent | Yes |     |
| applies_after_days | Int | Yes |     |
| recurring | Check | Yes | 0/1 |
| recurring_frequency_days | Int | No  | If recurring |
| max_penalty | Currency | No  | Optional cap |
| active | Check | Yes | 1   |

**G. DocType: Chama Contribution Waiver**

**Purpose**

Tracks waived obligations or penalties.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| member | Link(Chama Member) | Yes |
| obligation | Link(Chama Contribution Obligation) | Yes |
| waiver_type | Select | Yes |
| amount_waived | Currency | Yes |
| reason | Small Text | Yes |
| requested_by | Link(User) | Yes |
| approved_by | Link(User) | No  |
| status | Select | Yes |
| approved_at | Datetime | No  |

**Status Enum**

Draft  
Submitted  
Approved  
Rejected  
Cancelled

**4.2.5 STATE MACHINES (FORMAL)**

**A. Contribution Obligation State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Pending | Due | Scheduler / due_date reached | System | Today >= due_date | Member reminder |
| Due | Partially Paid | Payment allocation | System | 0 < paid < due | Update outstanding |
| Due | Paid | Payment allocation | System | paid == due | Mark settled |
| Due | Overdue | Scheduler / grace exceeded | System | Today > grace_end_date and outstanding > 0 | Notify member, consider penalty |
| Partially Paid | Paid | Payment allocation | System | outstanding == 0 | Mark settled |
| Partially Paid | Overdue | Scheduler | System | grace exceeded and outstanding > 0 | Notify |
| Due / Overdue / Partially Paid | Waived | Approved waiver | Chair/Treasurer | Waiver approved | Adjust outstanding |
| Any non-final | Cancelled | Admin correction | Admin | No dependent locked records | Audit log required |

**B. Payment State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Recorded | Allocated | Allocation complete | System/User | sum allocations == amount_received | Update obligations |
| Recorded | Partially Allocated | Allocation partial | System/User | allocations < amount_received | Leave unapplied credit |
| Allocated / Partially Allocated | Reversed | Reversal action | Treasurer/Admin | Valid reason | Reverse allocations |
| Recorded / Allocated | Flagged | Duplicate/suspicious detected | System/User | Rule hit | Notify reviewer |

**C. Waiver State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit | Treasurer | Reason present | Notify approver |
| Submitted | Approved | Approve | Chair / Treasurer if allowed | Within authority | Update obligation |
| Submitted | Rejected | Reject | Approver | —   | Notify requester |
| Draft / Submitted | Cancelled | Cancel | Requester/Admin | Not already approved | No financial change |

**4.2.6 SCHEDULE GENERATION LOGIC**

**A. Purpose**

At defined intervals, the system must generate obligations for all active members based on active contribution categories and Chama rules.

**B. Scheduler**

| **Job** | **Frequency** |
| --- | --- |
| Contribution cycle generation | Daily at 00:10 |
| Obligation due-state refresh | Daily at 00:20 |
| Overdue and penalty check | Daily at 00:30 |

**C. Pseudocode**

def generate_contribution_cycle(chama, target_date):  
categories = get_active_categories(chama, target_date)  
members = get_active_members(chama)  
cycle = create_cycle(chama, target_date)  
<br/>for member in members:  
for category in categories:  
if category_applies_to_member(category, member, target_date):  
amount = resolve_amount(category, member, target_date)  
due_date = resolve_due_date(category, cycle)  
grace_end = due_date + timedelta(days=category.grace_days)  
<br/>create_obligation(  
chama=chama,  
member=member,  
cycle=cycle,  
category=category,  
amount_due=amount,  
due_date=due_date,  
grace_end_date=grace_end,  
status="Pending"  
)

**D. Rules**

- only Active members receive normal recurring obligations
- Suspended members may still retain unpaid obligations but do not necessarily receive new optional ones unless rules allow
- Dormant member handling is configurable
- joining mid-cycle behavior is configurable:
    - full charge
    - prorated charge
    - next-cycle start

**4.2.7 PAYMENT ALLOCATION ENGINE**

This must be deterministic and auditable.

**A. Default Allocation Order**

Unless the Chama explicitly configures otherwise:

1.  Oldest overdue obligations
2.  Current due obligations
3.  Future obligations, only if prepayment allowed
4.  Unapplied credit balance if excess remains

**B. Allocation Scope**

Payments may be:

- unrestricted (system auto-allocates)
- category-targeted
- manually allocated by treasurer

**C. Allocation Algorithm**

def allocate_payment(payment, target_category=None):  
obligations = get_open_obligations(  
chama=payment.chama,  
member=payment.member,  
target_category=target_category,  
ordered_by=\["status_priority", "due_date", "creation"\]  
)  
<br/>remaining = payment.amount_received  
<br/>for ob in obligations:  
if remaining <= 0:  
break  
alloc = min(remaining, ob.amount_outstanding)  
create_allocation(payment, ob, alloc)  
ob.amount_paid += alloc  
update_obligation_status(ob)  
remaining -= alloc  
<br/>if remaining > 0:  
create_member_credit(payment.member, payment.chama, remaining)

**D. Allocation Status Priority**

| **Priority** | **Status** |
| --- | --- |
| 1   | Overdue |
| 2   | Due |
| 3   | Partially Paid |
| 4   | Pending (future allowed only if config says yes) |

**4.2.8 ACTION DEFINITIONS**

**A. Generate Contribution Cycle**

**Trigger**

Scheduled job or manual action by treasurer

**Input**

{  
"chama": "CH-0001",  
"target_period_start": "2026-04-01",  
"target_period_end": "2026-04-30"  
}

**Process**

- create cycle
- fetch applicable categories
- fetch applicable active members
- create obligations

**Output**

{  
"status": "success",  
"cycle_id": "CY-2026-04",  
"obligations_created": 245  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| CN001 | Contribution cycle already exists for this period |
| CN002 | No active contribution categories configured |
| CN003 | No eligible members found |

**B. Submit Contribution Payment**

**Input**

{  
"chama": "CH-0001",  
"member": "MB-0001",  
"amount_received": 5000,  
"payment_method": "Mobile Money",  
"payment_reference": "QWE123XYZ",  
"target_category": "Shares"  
}

**Process**

1.  validate member
2.  validate amount > 0
3.  detect possible duplicate
4.  create payment record
5.  allocate payment
6.  update obligation statuses
7.  notify member

**Output**

{  
"status": "success",  
"payment_id": "CPT-00045",  
"allocation_status": "Allocated",  
"allocated_total": 5000,  
"remaining_credit": 0  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| CN101 | Member not active or not found in Chama |
| CN102 | Invalid payment amount |
| CN103 | Duplicate payment reference suspected |
| CN104 | No eligible obligations available for targeted category |

**C. Request Waiver**

**Input**

{  
"obligation": "COB-00045",  
"waiver_type": "Penalty",  
"amount_waived": 200,  
"reason": "Committee-approved compassionate waiver"  
}

**Process**

- validate authority
- create waiver request
- route for approval if necessary

**Output**

{  
"status": "success",  
"waiver_id": "CWA-0003",  
"waiver_status": "Submitted"  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| CN201 | Waiver amount exceeds outstanding amount |
| CN202 | Reason is required |
| CN203 | User not authorized to request waiver |

**D. Reverse Payment**

**Input**

{  
"payment_id": "CPT-00045",  
"reason": "Duplicate mobile money posting"  
}

**Process**

- validate payment not already reversed
- create reversal payment
- reverse allocations
- recompute obligation statuses
- log audit

**Output**

{  
"status": "success",  
"reversal_id": "CPT-00046"  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| CN301 | Payment already reversed |
| CN302 | Payment not eligible for reversal |
| CN303 | Reason is required for reversal |

**4.2.9 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Member Contributions Dashboard (Mobile)**

**Purpose**

Show member-specific contribution summary.

**Sections**

**1\. Summary Card**

| **Field** | **Type** | **Visible To** | **Description** |
| --- | --- | --- | --- |
| total_due_now | Currency | Member | Sum of Due + Overdue outstanding |
| total_overdue | Currency | Member | Overdue balance |
| total_paid_this_cycle | Currency | Member |     |
| next_due_date | Date | Member | Earliest pending due |
| unapplied_credit | Currency | Member | Credit balance if any |

**2\. Contribution List**

| **Field** | **Type** |
| --- | --- |
| category_name | Data |
| amount_due | Currency |
| amount_paid | Currency |
| amount_outstanding | Currency |
| due_date | Date |
| status | Badge |

**3\. Actions**

- Pay Contribution
- View History
- View Receipt
- Raise Query (future)

**Behavior**

- default filter = current cycle
- allow filter by category and date range
- overdue items appear first
- status badge colors:
    - Paid = green
    - Due = blue
    - Overdue = red
    - Partially Paid = orange
    - Waived = gray

**B. Screen: Record Contribution Payment (Desk)**

**Fields**

| **Field Name** | **Type** | **Req** | **Editable By** | **Notes** |
| --- | --- | --- | --- | --- |
| member | Link(Chama Member) | Yes | Treasurer |     |
| payment_date | Datetime | Yes | Treasurer | default now |
| amount_received | Currency | Yes | Treasurer |     |
| payment_method | Select | Yes | Treasurer |     |
| payment_reference | Data | Cond. | Treasurer | required except allowed cash/manual adjustments |
| target_category | Link(Category) | No  | Treasurer | optional |
| received_into_account | Data | No  | Treasurer | wallet/bank/cashbook |
| remarks | Small Text | No  | Treasurer |     |

**Actions**

- Save as Recorded
- Save and Allocate
- Flag as Duplicate
- Reverse (if authorized)

**Validation Rules**

- member must be Active unless policy allows posting for Exited/Inactive historical settlement
- amount_received > 0
- suspected duplicates prompt warning and require explicit override

**C. Screen: Contribution Category Setup (Desk)**

**Fields**

As defined in Chama Contribution Category

**Additional UI Rules**

- if amount_type = Fixed, show default_amount mandatory
- if category_type = Penalty, hide normal frequency controls if rule-based generation only
- if active unchecked, block new cycle generation for this category

**D. Screen: Waiver Approval Screen (Desk)**

**Fields**

| **Field** | **Type** |
| --- | --- |
| obligation | Link |
| member | Link |
| waiver_type | Select |
| amount_waived | Currency |
| reason | Text |
| status | Select |
| requested_by | Link |
| approved_by | Link |

**Actions**

- Approve
- Reject
- Cancel

**4.2.10 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View own obligations | Yes | Yes | Yes | Limited | Yes | Yes |
| View all obligations in Chama | No  | Yes | Yes | Limited | Yes | Yes |
| Record payment | No  | Yes | No  | No  | No  | Yes |
| Allocate payment manually | No  | Yes | No  | No  | No  | Yes |
| Reverse payment | No  | Limited | No  | No  | No  | Yes |
| Request waiver | No  | Yes | Yes | No  | No  | Yes |
| Approve waiver | No  | Configurable | Yes | No  | No  | Yes |
| Edit category setup | No  | Limited | No  | No  | No  | Yes |
| Run cycle generation | No  | Yes | No  | No  | No  | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Obligation | amount_due | Read own | Read | Read | Read |
| Obligation | amount_paid | Read own | Read | Read | Read |
| Payment | payment_reference | Read own if on receipt | Read/Write | Read | Read |
| Waiver | approved_by | No  | Read | Write | Read |

**C. Chama Scope Enforcement**

All list views, reports, API queries, and link lookups must filter by:

doc.chama == current_user_selected_chama

**4.2.11 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| Contribution due soon | due_date - reminder_days | Member | App/SMS | contribution_due_reminder | Medium |
| Contribution overdue | grace expired | Member | App/SMS | contribution_overdue_alert | High |
| Payment received | payment allocated | Member | App | contribution_payment_received | Medium |
| Payment flagged duplicate | duplicate_flag set | Treasurer | App | contribution_duplicate_flagged | High |
| Waiver submitted | waiver submit | Approver | App | waiver_request_submitted | Medium |
| Waiver approved | waiver approve | Member/Treasurer | App | waiver_approved_notice | Medium |
| Cycle generated | cycle generation success | Treasurer | App | contribution_cycle_generated | Low |

**Example Template: contribution_due_reminder**

Reminder: Your {category_name} contribution of {amount_due} is due on {due_date} for {chama_name}.

**Example Template: contribution_overdue_alert**

Your {category_name} contribution of {amount_outstanding} is overdue. Penalties may apply after {grace_end_date}.

**4.2.12 API ENDPOINTS (FULL)**

**A. Get Member Contribution Summary**

GET /api/method/chama.contribution.get_member_summary

**Query Params**

- chama
- member
- cycle (optional)

**Response**

{  
"status": "success",  
"data": {  
"member": "MB-0001",  
"total_due_now": 5000,  
"total_overdue": 1000,  
"total_paid_this_cycle": 3000,  
"next_due_date": "2026-04-05",  
"unapplied_credit": 0,  
"obligations": \[  
{  
"obligation_id": "COB-0001",  
"category": "Shares",  
"amount_due": 5000,  
"amount_paid": 3000,  
"amount_outstanding": 2000,  
"status": "Partially Paid"  
}  
\]  
},  
"errors": \[\]  
}

**B. Submit Contribution Payment**

POST /api/method/chama.contribution.submit_payment

**Request**

{  
"chama": "CH-0001",  
"member": "MB-0001",  
"amount_received": 5000,  
"payment_method": "Mobile Money",  
"payment_reference": "QWE123XYZ",  
"target_category": "CCAT-0001"  
}

**Response**

{  
"status": "success",  
"data": {  
"payment_id": "CPT-0001",  
"allocation_status": "Allocated",  
"allocated_obligations": \[  
{  
"obligation": "COB-0001",  
"allocated_amount": 5000  
}  
\]  
},  
"errors": \[\]  
}

**C. Get Contribution History**

GET /api/method/chama.contribution.history

**Query Params**

- chama
- member
- from_date
- to_date
- category (optional)

**D. Run Cycle Generation**

POST /api/method/chama.contribution.generate_cycle

**Request**

{  
"chama": "CH-0001",  
"period_start": "2026-04-01",  
"period_end": "2026-04-30"  
}

**Authorization**

Treasurer/Admin only

**E. Request Waiver**

POST /api/method/chama.contribution.request_waiver

**F. Approve Waiver**

POST /api/method/chama.contribution.approve_waiver

**G. Reverse Payment**

POST /api/method/chama.contribution.reverse_payment

**4.2.13 REPORTS**

**A. Report: Member Contribution Statement**

**Filters**

- Chama
- Member
- Date Range
- Category

**Columns**

- Date
- Cycle
- Category
- Amount Due
- Amount Paid
- Amount Waived
- Outstanding
- Status

**B. Report: Contribution Compliance Report**

**Metrics**

- expected total
- paid total
- overdue total
- compliance rate

**Formula**

compliance_rate = paid_total / expected_total

**C. Report: Overdue Contributions Report**

**Columns**

- Member
- Category
- Due Date
- Grace End
- Outstanding
- Days Overdue

**D. Report: Payment Register**

**Columns**

- Payment ID
- Member
- Date
- Method
- Reference
- Amount
- Status

**4.2.14 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Contribution Category | Required |
| Custom DocType | Chama Contribution Cycle | Required |
| Custom DocType | Chama Contribution Obligation | Required |
| Custom DocType | Chama Contribution Payment | Required |
| Child Table | Contribution Payment Allocation | Required |
| Custom DocType | Chama Penalty Rule | Shared use |
| Custom DocType | Chama Contribution Waiver | Required |
| Scheduled Job | generate_contribution_cycle | Required |
| Scheduled Job | refresh_due_and_overdue_status | Required |
| Scheduled Job | apply_penalties | Required |
| Notifications | due/overdue/payment/waiver | Required |
| Reports | member statement/compliance/overdue/register | Required |

**4.2.15 SERVER LOGIC / HOOKS**

**A. On Payment Validate**

def validate(self):  
ensure_member_matches_chama(self.member, self.chama)  
detect_possible_duplicate(self)

**B. On Payment Submit / Save**

def on_submit(self):  
auto_allocate_payment(self)  
notify_member_payment_received(self)

**C. Daily Overdue Refresh**

def refresh_due_and_overdue_status():  
obligations = get_open_obligations()  
for ob in obligations:  
if today() >= ob.due_date and ob.status == "Pending":  
ob.status = "Due"  
if today() > ob.grace_end_date and ob.amount_outstanding > 0:  
ob.status = "Overdue"  
ob.save()

**D. Penalty Application**

def apply_penalties():  
overdue = get_overdue_without_penalty()  
for ob in overdue:  
if ob.category.penalty_rule:  
create_penalty_obligation(ob)

**4.2.16 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Overpayment | amount_received > eligible obligations | Create unapplied credit or future allocation | Yes |
| Wrong category payment | user-targeted category has no open due | Prompt confirmation or reallocate | Yes |
| Duplicate payment | same reference + same member + close time window | Flag, allow review | Yes |
| Missed multiple cycles | open obligations > 1 cycle | Allocate oldest first | Implicit |
| Member joins mid-cycle | join_date inside cycle | Apply prorate/full/next-cycle policy | Yes |
| Member exited but historical payment posted | status Exited | Allow only if settlement mode | Yes |
| Reversal after report close | period closed | Allow with adjustment record in current open period or controlled reopen | Yes |
| Negative outstanding due to bug/manual corruption | sanity check | Block save, require admin repair | Yes |

**4.2.17 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Loans | Eligibility uses contribution history, outstanding contributions, and contribution compliance score |
| Reconciliation | Expected cash inflow derives from contribution payments |
| Notifications | Due/overdue/payment events feed notification queue |
| Budgeting | Contribution categories and totals influence planned inflow |
| Member Lifecycle | Active members determine obligation generation |
| Analytics | Compliance rates and delinquency metrics come from obligations/payments |

**4.2.18 CRITICAL IMPLEMENTATION RULES**

- No obligation record may exist without chama, member, category, cycle, amount_due, and due_date
- No payment may be hard-deleted after posting
- Allocation must always be reconstructible from payment + allocation rows
- Paid totals on obligations must be derived from allocations or updated transactionally, never manually edited
- Reversals must create compensating records, not overwrite history
- All contribution records must be Chama-filtered in every API, report, and view
- Member-facing totals must exactly match report totals for the same filters

## MODULE 4.3 — DISBURSEMENTS

**4.3.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Loan disbursement core | Frappe Lending |
| Non-loan disbursement requests | Custom |
| Approval workflows | ERPNext Workflow + custom rules |
| Budget checks | Custom + Budget module |
| Payment execution records | Custom, optionally linked to ERPNext accounting later |
| Notifications | Shared notification engine |
| Reporting | ERPNext reports + custom logic |

**4.3.2 MODULE PURPOSE**

The Disbursements module shall manage all controlled outflows of value from a Chama, including:

- loan disbursements
- welfare payouts
- benevolent support
- bonuses/dividends
- reimbursements
- investment purchases or distributions
- exception or committee-approved payouts

This module must explicitly separate:

1.  **Disbursement Request**  
    the request or basis to release funds
2.  **Disbursement Approval**  
    the governance decision allowing release
3.  **Disbursement Execution**  
    the actual transfer/posting of funds

That separation is mandatory.

**4.3.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall use a hybrid approach:

**Reuse from ERPNext / Frappe / Lending**

- Workflow engine
- Roles and permissions
- Reports
- Notifications
- File attachments
- audit/versioning patterns
- Frappe Lending loan disbursement lifecycle for loans

**Custom Chama layer**

- non-loan disbursement request model
- approval thresholds and Chama-specific routing
- budget enforcement
- beneficiary and payout basis model
- payout execution record
- reversal and exception handling
- member-facing payout visibility

**Rule**

Loan disbursement shall not duplicate Frappe Lending’s loan booking/disbursement engine.  
The Chama layer shall wrap it with:

- Chama checks
- Chama approvals
- Chama notifications
- Chama reporting context

**4.3.4 DISBURSEMENT TYPES**

The system shall support the following normalized disbursement types:

| **Type Code** | **Label** | **Description** |
| --- | --- | --- |
| LOAN | Loan Disbursement | Funds advanced to borrower from approved loan |
| WELFARE | Welfare Payout | Welfare/compassionate support |
| BENEFIT | Benefit Payout | Member support outside welfare |
| BONUS | Bonus / Dividend | Profit or surplus distribution |
| REIMB | Reimbursement | Reimbursement of approved expense |
| INVEST_OUT | Investment Outflow | Purchase or capital deployment |
| INVEST_RET | Investment Return Distribution | Return paid to members |
| ADJUST | Adjustment Payout | Controlled correction |

**4.3.5 DATA MODEL (FULL)**

**A. DocType: Chama Disbursement Request**

**Purpose**

Represents a request or approved basis for a payout, except where loan disbursement is purely referenced from Lending.

**DocType Type**

- Custom DocType
- Is Submittable: Yes
- Workflow Enabled: Yes

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Default** | **Validation** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| name | Request ID | Data (Auto) | Yes | Auto | Unique | Example: DBR-0001 |
| chama | Chama | Link(Chama) | Yes | —   | Required | Tenant anchor |
| request_type | Request Type | Select | Yes | WELFARE | Enum from supported types |     |
| beneficiary_type | Beneficiary Type | Select | Yes | Member | Member / Vendor / External / Group Fund |     |
| beneficiary_member | Beneficiary Member | Link(Chama Member) | No  | —   | Required if beneficiary_type = Member |     |
| beneficiary_name | Beneficiary Name | Data | No  | —   | Required if non-member/manual |     |
| related_module | Related Module | Select | No  | —   | Loan / Budget / Investment / Welfare / Expense / Other |     |
| related_reference | Related Reference | Dynamic Link | No  | —   | Optional linkage |     |
| amount_requested | Amount Requested | Currency | Yes | —   | \> 0 |     |
| amount_recommended | Amount Recommended | Currency | No  | —   | \>= 0 | Filled during review |
| amount_approved | Amount Approved | Currency | No  | —   | \>= 0 and <= requested unless justified |     |
| request_reason | Request Reason | Small Text | Yes | —   | Not empty |     |
| supporting_document | Attach | No  | —   | Optional |     |     |
| request_date | Datetime | Yes | Now | —   |     |     |
| budget_item | Link(Chama Budget Item or custom reference) | No  | —   | If budget-controlled |     |     |
| budget_check_status | Select | Yes | Not Checked | Not Checked / Within Budget / Over Budget / Blocked |     |     |
| workflow_state | Data / Workflow | Yes | Draft | —   | ERPNext workflow state |     |
| operational_status | Select | Yes | Draft | Enum below |     |     |
| submitted_by | Link(User) | Yes | Session User | —   |     |     |
| approved_by | Link(User) | No  | —   | Filled on approval |     |     |
| approval_timestamp | Datetime | No  | —   |     |     |     |
| execution_required | Check | Yes | 1   | —   | Some approvals may not execute immediately |     |
| notes | Small Text | No  | —   |     |     |     |

**Constraints**

validate():  
if beneficiary_type == "Member" and not beneficiary_member:  
frappe.throw("Beneficiary Member is required")  
if beneficiary_type != "Member" and not beneficiary_name:  
frappe.throw("Beneficiary Name is required")  
if amount_requested <= 0:  
frappe.throw("Amount Requested must be greater than zero")

**B. DocType: Chama Disbursement Execution**

**Purpose**

Represents the actual payout event.

**This is the financial execution object and must never be hard-deleted.**

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Default** | **Validation** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| name | Execution ID | Data (Auto) | Yes | Auto | Unique | Example: DBX-0001 |
| chama | Chama | Link(Chama) | Yes | —   | Required |     |
| disbursement_request | Disbursement Request | Link(Chama Disbursement Request) | No  | —   | Optional for loan-linked cases |     |
| execution_type | Execution Type | Select | Yes | Manual | Manual / Loan / Automated / Adjustment |     |
| beneficiary_type | Beneficiary Type | Select | Yes | Member | Mirrors request |     |
| beneficiary_member | Beneficiary Member | Link(Chama Member) | No  | —   |     |     |
| beneficiary_name | Beneficiary Name | Data | No  | —   |     |     |
| amount_executed | Currency | Yes | —   | \> 0 |     |     |
| execution_date | Datetime | Yes | Now | —   |     |     |
| payment_method | Select | Yes | Mobile Money | Mobile Money / Bank / Cash / Internal Transfer / Other |     |     |
| payment_reference | Data | No  | —   | Recommended except cash | M-Pesa / bank ref |     |
| source_fund | Select / Link | Yes | General Fund | Shares / Welfare / Investment / Reserve / Loan Pool / Other |     |     |
| execution_status | Select | Yes | Pending | Pending / Executed / Failed / Reversed / Flagged |     |     |
| executed_by | Link(User) | Yes | Session User | —   |     |     |
| failure_reason | Small Text | No  | —   | For failed status |     |     |
| reversal_of | Link(Chama Disbursement Execution) | No  | —   | For reversals |     |     |
| remarks | Small Text | No  | —   |     |     |     |

**Constraints**

validate():  
if execution_status == "Failed" and not failure_reason:  
frappe.throw("Failure reason is required for failed execution")

**C. DocType: Chama Approval Rule**

**Purpose**

Defines who must approve what kinds of disbursements and at what thresholds.

**Fields**

| **Field** | **Type** | **Req** | **Notes** |
| --- | --- | --- | --- |
| name | Data (Auto) | Yes |     |
| chama | Link(Chama) | Yes |     |
| request_type | Select | Yes | Disbursement type |
| min_amount | Currency | Yes |     |
| max_amount | Currency | No  | Optional upper bound |
| approval_level | Select | Yes | Treasurer / Chair / Committee / Voting |
| require_budget_check | Check | Yes | 1/0 |
| require_supporting_document | Check | Yes | 1/0 |
| active | Check | Yes | 1   |

**D. DocType: Chama Disbursement Reversal**

**Purpose**

Tracks reversal metadata separate from the execution if needed for control review.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| original_execution | Link(Chama Disbursement Execution) | Yes |
| reversal_execution | Link(Chama Disbursement Execution) | Yes |
| reason | Small Text | Yes |
| requested_by | Link(User) | Yes |
| approved_by | Link(User) | No  |
| created_on | Datetime | Yes |

**E. Loan Disbursement Link Strategy**

For loan disbursements:

- the authoritative loan state and disbursement remain in Frappe Lending
- a Chama-side execution mirror or reference record may be created for unified reporting

**Recommended lightweight mirror fields**

| **Field** | **Type** |
| --- | --- |
| loan_reference | Link(Loan) |
| lending_disbursement_reference | Data / Link |
| chama | Link(Chama) |
| member | Link(Chama Member) |
| amount | Currency |
| status | Select |
| execution_date | Datetime |

This avoids rebuilding loan disbursement logic while preserving Chama visibility.

**4.3.6 STATE MACHINES (FORMAL)**

**A. Disbursement Request State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit | Member/Treasurer | Required fields present | Notify reviewer |
| Submitted | Under Review | Open review | Treasurer/System | —   |     |
| Under Review | Pending Approval | Escalate | Treasurer/System | Threshold or rule requires | Notify approver |
| Under Review / Pending Approval | Approved | Approve | Treasurer/Chair/Committee | Rules satisfied | Set approved amount |
| Under Review / Pending Approval | Rejected | Reject | Approver | —   | Notify requester |
| Approved | Ready for Execution | Auto | System | Budget OK, funds OK, approval complete | Notify executor |
| Ready for Execution | Executed | Execute | Treasurer/System | Execution succeeded | Create execution record |
| Ready for Execution | Failed | Execute | Treasurer/System | Failure encountered | Log failure |
| Any pre-final | Cancelled | Cancel | Authorized user | Not already executed | Audit log |

**B. Disbursement Execution State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Pending | Executed | Success | Treasurer/System | Funds available, method accepted | Notify beneficiary |
| Pending | Failed | Failure | Treasurer/System | Provider failure or validation issue | Notify ops if critical |
| Executed | Reversed | Reversal | Treasurer/Admin | Approved reason | Create compensating entry |
| Pending / Executed | Flagged | Manual/system review | Treasurer/System | Duplicate or anomaly | Alert reviewer |

**C. Loan-Linked State Overlay**

| **Lending Loan State** | **Chama View** |
| --- | --- |
| Approved | Ready for Disbursement |
| Disbursed | Executed |
| Cancelled / not disbursed | Cancelled / Failed as applicable |

**4.3.7 APPROVAL ENGINE**

**A. Approval Resolution Logic**

def resolve_disbursement_approval(chama, request_type, amount):  
rules = get_active_approval_rules(chama, request_type)  
matched = find_rule_for_amount(rules, amount)  
if not matched:  
return "Chair"  
return matched.approval_level

**B. Standard Approval Levels**

| **Level** | **Meaning** |
| --- | --- |
| Treasurer | Treasurer may approve directly |
| Chair | Chair approval required |
| Committee | Requires committee action / meeting evidence |
| Voting | Requires formal proposal + voting result |

**C. Approval Conditions**

- required document attached if rule requires
- budget check passed if budget-controlled
- beneficiary resolved
- duplicate request check passed
- for member payouts, member belongs to same Chama unless policy allows external beneficiary
- for loan-linked requests, Lending loan is in eligible state

**4.3.8 BUDGET ENFORCEMENT LOGIC**

This module must integrate with Budgeting.

**A. Budget Check Modes**

| **Mode** | **Behavior** |
| --- | --- |
| Strict | Block if no budget or overrun |
| Warning | Allow but flag and require higher approval |
| Off | No budget enforcement |

**B. Check Formula**

remaining_budget = allocated_amount - actual_disbursed_to_item

**C. Enforcement Pseudocode**

def check_budget(request):  
if not request.budget_item:  
return "Not Checked"  
<br/>remaining = get_remaining_budget(request.budget_item)  
if request.amount_requested <= remaining:  
return "Within Budget"  
<br/>if get_budget_mode(request.chama) == "Strict":  
return "Blocked"  
<br/>return "Over Budget"

**D. Side Effects**

- Within Budget → proceed normally
- Over Budget → escalate approval
- Blocked → cannot move to Approved/Ready for Execution

**4.3.9 ACTION DEFINITIONS**

**A. Submit Disbursement Request**

**Input**

{  
"chama": "CH-0001",  
"request_type": "WELFARE",  
"beneficiary_type": "Member",  
"beneficiary_member": "MB-0007",  
"amount_requested": 8000,  
"request_reason": "Hospital support",  
"budget_item": "BUD-ITEM-004"  
}

**Process**

1.  validate fields
2.  resolve beneficiary
3.  run duplicate request check
4.  run budget check
5.  resolve approval level
6.  create request
7.  notify reviewer

**Output**

{  
"status": "success",  
"data": {  
"request_id": "DBR-0008",  
"workflow_state": "Submitted",  
"approval_required_level": "Chair",  
"budget_check_status": "Within Budget"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| DB001 | Invalid beneficiary |
| DB002 | Amount must be greater than zero |
| DB003 | Budget blocked this request |
| DB004 | Similar pending request already exists |

**B. Approve Disbursement Request**

**Input**

{  
"request_id": "DBR-0008",  
"approved_amount": 7500,  
"approval_note": "Reduced to approved welfare limit"  
}

**Process**

- validate approver authority
- ensure request in approvable state
- ensure approved_amount valid
- set Approved
- if execution can proceed, mark Ready for Execution

**Output**

{  
"status": "success",  
"data": {  
"request_id": "DBR-0008",  
"workflow_state": "Approved",  
"operational_status": "Ready for Execution"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| DB101 | User not authorized to approve |
| DB102 | Approved amount invalid |
| DB103 | Request not in approvable state |

**C. Execute Disbursement**

**Input**

{  
"request_id": "DBR-0008",  
"payment_method": "Mobile Money",  
"payment_reference": "MP12345X",  
"source_fund": "Welfare Fund"  
}

**Process**

1.  validate Ready for Execution
2.  validate funds available
3.  create execution record
4.  mark request Executed
5.  notify beneficiary
6.  feed reconciliation/reporting

**Output**

{  
"status": "success",  
"data": {  
"execution_id": "DBX-0021",  
"execution_status": "Executed"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| DB201 | Request not ready for execution |
| DB202 | Insufficient available funds |
| DB203 | Payment method/reference invalid |

**D. Reverse Disbursement**

**Input**

{  
"execution_id": "DBX-0021",  
"reason": "Duplicate payout"  
}

**Process**

- validate not already reversed
- validate user authority
- create compensating reversal execution
- create reversal record
- update statuses and logs

**Output**

{  
"status": "success",  
"data": {  
"reversal_execution_id": "DBX-0022",  
"reversal_record_id": "DBREV-0001"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| DB301 | Execution already reversed |
| DB302 | Reason is required |
| DB303 | User not authorized to reverse |

**4.3.10 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Member Disbursement Request (Mobile)**

**Purpose**

Allow members to request welfare/benefit/reimbursement payouts where allowed.

**Fields**

| **Field** | **Type** | **Req** | **Visible To** | **Behavior** |
| --- | --- | --- | --- | --- |
| request_type | Select | Yes | Member | Filtered to allowed member request types |
| amount_requested | Currency | Yes | Member | Must be > 0 |
| request_reason | Text Area | Yes | Member | Required |
| supporting_document | Attach | No  | Member | Optional or required by rule |
| beneficiary_member | Hidden/self | Conditional | Member | Auto-self for member requests |
| beneficiary_name | Hidden | No  | Member | Not normally shown |

**Actions**

- Save Draft
- Submit Request

**Validation**

- member must be Active unless policy allows otherwise
- request_type must be allowed for member self-service
- amount within configured maximum or mark escalation

**B. Screen: Disbursement Review (Desk)**

**Purpose**

Used by Treasurer/Chair/Committee reviewer.

**Sections**

**1\. Request Summary**

| **Field** | **Description** |
| --- | --- |
| request_id | Request identifier |
| type | Disbursement type |
| beneficiary | Member/vendor/external |
| amount_requested | Requested amount |
| amount_recommended | Review amount |
| amount_approved | Final amount |
| reason | Request basis |
| support docs | Attachments |

**2\. Control Checks**

| **Field** | **Description** |
| --- | --- |
| budget_check_status | Within budget / over budget / blocked |
| duplicate_check | Similar requests indicator |
| approval_required_level | Treasurer / Chair / Committee / Voting |
| funds_available_indicator | Yes/No |
| related_reference | linked loan/meeting/budget/etc |

**3\. Actions**

- Recommend Amount
- Approve
- Reject
- Escalate
- Request More Information

**C. Screen: Disbursement Execution (Desk)**

**Purpose**

Actual release of funds after approval.

**Fields**

| **Field** | **Type** | **Req** | **Notes** |
| --- | --- | --- | --- |
| request_id | Link | Yes | must be Ready for Execution |
| payment_method | Select | Yes |     |
| payment_reference | Data | Cond. | required except allowed cash flows |
| amount_executed | Currency | Yes | defaults to approved amount |
| source_fund | Select | Yes |     |
| execution_date | Datetime | Yes | default now |
| remarks | Small Text | No  |     |

**Actions**

- Execute
- Mark Failed
- Cancel Pending

**D. Screen: Disbursement Log**

**Purpose**

Operational and audit review.

**Columns**

- Execution ID
- Request ID
- Type
- Beneficiary
- Amount
- Method
- Reference
- Status
- Date
- Executed By

**Filters**

- Chama
- Date range
- Type
- Status
- Beneficiary
- Source fund

**4.3.11 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| Create self-service request | Yes (limited types) | Yes | No  | No  | No  | Yes |
| View own request | Yes | Yes | Yes | Limited | Yes | Yes |
| View all requests in Chama | No  | Yes | Yes | Limited | Yes | Yes |
| Recommend amount | No  | Yes | No  | No  | No  | Yes |
| Approve ordinary request | No  | Configurable | Yes | No  | No  | Yes |
| Approve over-threshold request | No  | No  | Yes | No  | No  | Yes |
| Execute payout | No  | Yes | No  | No  | No  | Yes |
| Reverse execution | No  | Limited | No  | No  | No  | Yes |
| View full execution log | No  | Yes | Yes | No  | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Request | amount_requested | Read own | Read/Write review | Read | Read |
| Request | amount_approved | Read own after decision | Write | Write | Read |
| Execution | payment_reference | Read own if beneficiary | Read/Write | Read | Read |
| Request | budget_check_status | No  | Read | Read | Read |

**C. Chama Scope Rule**

All disbursement requests and executions must be filtered by active Chama context:

doc.chama == current_user_selected_chama

**4.3.12 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| Request submitted | submit | Reviewer | App/SMS | disbursement_request_submitted | Medium |
| Request escalated | escalation | Higher approver | App | disbursement_request_escalated | Medium |
| Request approved | approve | Requester/beneficiary | App/SMS | disbursement_request_approved | Medium |
| Request rejected | reject | Requester | App | disbursement_request_rejected | Medium |
| Ready for execution | ready state | Treasurer/executor | App | disbursement_ready_for_execution | High |
| Executed | execution success | Beneficiary | App/SMS | disbursement_executed | High |
| Failed | execution failure | Treasurer/Admin | App | disbursement_execution_failed | High |
| Reversed | reversal | Beneficiary/Treasurer | App | disbursement_reversed | High |

**Example Template: disbursement_executed**

Your {request_type} disbursement of {amount_executed} has been completed on {execution_date}.

**4.3.13 API ENDPOINTS (FULL)**

**A. Submit Disbursement Request**

POST /api/method/chama.disbursement.submit_request

**Request**

{  
"chama": "CH-0001",  
"request_type": "WELFARE",  
"beneficiary_type": "Member",  
"beneficiary_member": "MB-0007",  
"amount_requested": 8000,  
"request_reason": "Hospital support"  
}

**Response**

{  
"status": "success",  
"data": {  
"request_id": "DBR-0008",  
"workflow_state": "Submitted"  
},  
"errors": \[\]  
}

**B. Review / Recommend**

POST /api/method/chama.disbursement.recommend

**Request**

{  
"request_id": "DBR-0008",  
"amount_recommended": 7500,  
"note": "Within welfare cap"  
}

**C. Approve Request**

POST /api/method/chama.disbursement.approve

**D. Reject Request**

POST /api/method/chama.disbursement.reject

**E. Execute Disbursement**

POST /api/method/chama.disbursement.execute

**F. Reverse Execution**

POST /api/method/chama.disbursement.reverse

**G. Member Disbursement History**

GET /api/method/chama.disbursement.member_history?chama=CH-0001&member=MB-0007

**H. Operational Log**

GET /api/method/chama.disbursement.log?chama=CH-0001&from_date=2026-04-01&to_date=2026-04-30

**4.3.14 REPORTS**

**A. Report: Disbursement Register**

**Columns**

- Request ID
- Execution ID
- Type
- Beneficiary
- Requested
- Approved
- Executed
- Method
- Status
- Date

**B. Report: Welfare Support Report**

**Filters**

- Chama
- Period
- Beneficiary
- Status

**Purpose**

Track welfare-related support for transparency and committee review.

**C. Report: Bonus / Dividend Distribution Report**

**Columns**

- Member
- Basis
- Approved Amount
- Executed Amount
- Date

**D. Report: Failed / Reversed Disbursements Report**

**Purpose**

Operational control and audit review.

**4.3.15 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Disbursement Request | Required |
| Custom DocType | Chama Disbursement Execution | Required |
| Custom DocType | Chama Approval Rule | Required |
| Custom DocType | Chama Disbursement Reversal | Recommended |
| Workflow | Disbursement Approval | Required |
| Reports | Register / welfare / bonus / failed-reversed | Required |
| Notifications | submit / approve / reject / execute / fail / reverse | Required |
| Shared Integration | Budget module checks | Required |
| Shared Integration | Lending loan disbursement reference | Required for loan cases |

**4.3.16 WORKFLOW CONFIGURATION**

**Workflow Name: Disbursement Request Approval**

| **State** | **Doc Status** | **Allow Edit By** | **Transition Action** |
| --- | --- | --- | --- |
| Draft | 0   | Creator / Treasurer | Submit |
| Submitted | 0   | Treasurer | Start Review |
| Under Review | 0   | Treasurer | Recommend / Escalate / Reject |
| Pending Approval | 0   | Chair/Committee | Approve / Reject |
| Approved | 1 or controlled | System/Treasurer | Ready for Execution |
| Rejected | 1 or closed | No edit | End |
| Cancelled | 2-style logical cancel | No edit | End |

Note: Exact docstatus usage may vary depending on whether you want request submission to lock editing early; implementation should preserve auditability.

**4.3.17 SERVER LOGIC / HOOKS**

**A. Validate Request**

def validate(self):  
ensure_chama_consistency(self)  
detect_duplicate_request(self)  
self.budget_check_status = check_budget(self)  
self.approval_required_level = resolve_disbursement_approval(  
self.chama, self.request_type, self.amount_requested  
)

**B. On Approval**

def on_update_after_submit(self):  
if self.workflow_state == "Approved":  
self.amount_approved = self.amount_approved or self.amount_requested  
self.operational_status = "Ready for Execution"  
notify_ready_for_execution(self)

**C. Execute**

def execute_disbursement(request, method, reference):  
ensure_ready(request)  
ensure_funds_available(request)  
execution = create_execution_record(request, method, reference)  
mark_request_executed(request, execution)  
notify_beneficiary(execution)

**D. Reverse**

def reverse_disbursement(execution, reason):  
ensure_reversible(execution)  
reversal = create_reversal_execution(execution, reason)  
create_reversal_record(execution, reversal, reason)

**4.3.18 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Insufficient funds | available fund < approved amount | Block execution | Yes |
| Duplicate request | same beneficiary + type + close time + amount | Flag and require review | Yes |
| Partial payout | executed < approved | Allow only if policy/config permits; remaining tracked | Yes |
| Beneficiary not found for member payout | missing member link | Block | Yes |
| Supporting doc missing where required | rule check | Block submit/approve | Yes |
| Reversal after period close | closed period | Create current-period compensating reversal or controlled reopen | Yes |
| Loan request approved but Lending disbursement fails | callback/result mismatch | Mark failed, keep loan pending review | Yes |
| Budget item exhausted after approval but before execution | fresh check on execute | Block or escalate | Yes |
| External beneficiary typo | data validation/manual review | Require confirmation for non-member payouts | Yes |

**4.3.19 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Loans | Approved loans can produce loan disbursement events |
| Budgeting | Budget limits can block or escalate requests |
| Reconciliation | Executed disbursements reduce expected balance |
| Notifications | Requests/approvals/execution/failure feed queue |
| Meetings / Voting | Committee or formal approvals may be required |
| Investments | Investment purchases and returns use disbursement flows |
| Member Lifecycle | Beneficiary validity depends on member status |

**4.3.20 CRITICAL IMPLEMENTATION RULES**

- No disbursement may be executed without a traceable approved basis
- Loan disbursement logic must not replace or fork Lending core disbursement behavior
- Every executed payout must produce an immutable execution record
- Reversals must create compensating records, never overwrite the original
- Funds availability must be checked at execution time, not only at request time
- All disbursement records must include chama
- Beneficiary-facing status must exactly match operational records
- Approval thresholds must be configurable per Chama and request type

## MODULE 4.4 — RECONCILIATION & FINANCIAL STATEMENTS

**4.4.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Source transactions | Contributions / Disbursements / Loans / Investments |
| Reconciliation control records | Custom |
| Statement generation | Custom + ERPNext reports |
| Balance input / source capture | Custom |
| Variance resolution / adjustment controls | Custom |
| Notifications | Shared notification engine |
| Reporting / exports | ERPNext reports + custom logic |

**4.4.2 MODULE PURPOSE**

The Reconciliation & Financial Statements module shall manage:

- expected balance calculation from system transactions
- actual balance capture from operational money sources
- comparison between expected and actual balances
- discrepancy creation and investigation
- controlled adjustment entries
- monthly / periodic close
- statement generation for members and Chamas
- audit-ready evidence of financial position

This module must explicitly separate:

1.  **Expected Position**  
    what the system calculates should exist
2.  **Actual Position**  
    what physically or externally exists in bank/mobile/cash
3.  **Variance**  
    the difference between expected and actual
4.  **Resolution**  
    the formal correction, explanation, or acceptance of that difference

That separation is mandatory.

**4.4.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall primarily use custom DocTypes because standard ERPNext accounting/reporting features do not, by themselves, provide the Chama-specific reconciliation workflow required here.

**Reuse from ERPNext / Frappe**

- reports
- query reports / script reports
- dashboards / workspaces
- permissions
- workflow where controlled approvals are needed
- exports
- file attachments
- scheduler
- audit/version patterns

**Reuse from Frappe Lending**

- loan balances and repayment events as source transaction inputs only

**Custom Chama layer**

- reconciliation run / snapshot records
- actual balance capture
- variance analysis
- discrepancy issue management
- adjustment records
- period close logic
- Chama statement generation
- member statement generation
- expected balance formulas

**4.4.4 CORE FINANCIAL DEFINITIONS**

**A. Expected Balance**

For a defined Chama and valuation date:

Expected Balance =  
Opening Balance  
\+ Contribution Payments Received  
\+ Loan Repayments Received  
\+ Investment Returns Received  
\+ Other Approved Inflows  
\- Disbursements Executed  
\- Loan Disbursements Executed  
\- Investment Outflows Executed  
\- Other Approved Outflows  
± Approved Adjustments

This is not a bank balance.  
This is the system-calculated balance.

**B. Actual Balance**

Actual Balance shall be captured per fund source or holding channel:

- bank account balance
- mobile money wallet balance
- cash on hand / cashbox
- other configured holding accounts

Actual balance may be captured:

- manually
- via imported statement process
- via future API integration

**C. Variance**

Variance = Actual Balance - Expected Balance

Interpretation:

- 0 → balanced
- positive → unexplained excess or missing outflow
- negative → unexplained shortage or missing inflow

**D. Statement Period**

A statement period is a bounded reporting window:

- monthly
- quarterly
- annual
- ad hoc

**4.4.5 DATA MODEL (FULL)**

**A. DocType: Chama Financial Period**

**Purpose**

Defines a reporting/reconciliation period for a Chama.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Period ID | Data (Auto) | Yes | Example FP-2026-04 |
| chama | Chama | Link(Chama) | Yes |     |
| period_name | Period Name | Data | Yes | Example April 2026 |
| period_start | Period Start | Date | Yes |     |
| period_end | Period End | Date | Yes |     |
| status | Status | Select | Yes | Draft / Open / Closing / Closed / Archived |
| opened_by | Link(User) | No  |     |     |
| opened_on | Datetime | No  |     |     |
| closed_by | Link(User) | No  |     |     |
| closed_on | Datetime | No  |     |     |
| closing_notes | Small Text | No  |     |     |

**Constraints**

validate():  
if period_end < period_start:  
frappe.throw("Period End cannot be before Period Start")

**Status Enum**

Draft  
Open  
Closing  
Closed  
Archived

**B. DocType: Chama Reconciliation Run**

**Purpose**

Represents one reconciliation attempt or snapshot for a Chama on a given date.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Reconciliation ID | Data (Auto) | Yes | Example REC-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| financial_period | Link(Chama Financial Period) | No  | Optional if ad hoc |     |
| reconciliation_date | Datetime | Yes | Snapshot date/time |     |
| expected_total_balance | Currency | Yes | System-calculated |     |
| actual_total_balance | Currency | Yes | Captured sum |     |
| total_variance | Currency | Yes | actual - expected |     |
| status | Select | Yes | Open / Balanced / Discrepancy / Resolved / Closed |     |
| created_by | Link(User) | Yes |     |     |
| reviewed_by | Link(User) | No  |     |     |
| approved_by | Link(User) | No  |     |     |
| notes | Small Text | No  |     |     |

**Status Enum**

Open  
Balanced  
Discrepancy  
Resolved  
Closed

**C. Child Table: Reconciliation Source Balance**

**Parent**

Chama Reconciliation Run

**Purpose**

Captures expected and actual balances by source.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| source_type | Source Type | Select | Yes | Bank / Mobile Money / Cash / Other |
| source_name | Source Name | Data / Link | Yes | Account/wallet/cashbox label |
| expected_balance | Currency | Yes |     |     |
| actual_balance | Currency | Yes |     |     |
| variance | Currency | Yes | actual - expected |     |
| input_method | Select | Yes | Manual / Import / API |     |
| evidence_attachment | Attach | No  | Statement/screenshot/upload |     |
| notes | Small Text | No  |     |     |

**D. DocType: Chama Reconciliation Issue**

**Purpose**

Represents a discrepancy or unresolved financial difference identified during reconciliation.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Issue ID | Data (Auto) | Yes | Example RCI-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| reconciliation_run | Link(Chama Reconciliation Run) | Yes |     |     |
| issue_type | Select | Yes | Missing Inflow / Missing Outflow / Duplicate / Timing Difference / Unknown / Source Mismatch |     |
| source_type | Select | No  | Bank / Mobile / Cash / Other |     |
| amount | Currency | Yes | Absolute issue amount |     |
| description | Small Text | Yes |     |     |
| suspected_cause | Small Text | No  |     |     |
| status | Select | Yes | Open / Investigating / Adjusted / Explained / Rejected / Closed |     |
| owner_user | Link(User) | No  | Who is investigating |     |
| opened_on | Datetime | Yes |     |     |
| resolved_on | Datetime | No  |     |     |
| resolution_summary | Small Text | No  |     |     |

**Status Enum**

Open  
Investigating  
Adjusted  
Explained  
Rejected  
Closed

**E. DocType: Chama Adjustment Entry**

**Purpose**

Represents a controlled non-destructive correction or balancing entry.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Adjustment ID | Data (Auto) | Yes | Example ADJ-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| financial_period | Link(Chama Financial Period) | No  |     |     |
| reconciliation_issue | Link(Chama Reconciliation Issue) | No  | Optional but preferred |     |
| adjustment_type | Select | Yes | Missing Inflow / Missing Outflow / Reclassification / Reversal / Carry Forward / Manual Correction |     |
| direction | Select | Yes | Increase Balance / Decrease Balance / Neutral Reclass |     |
| amount | Currency | Yes | \> 0 |     |
| effective_date | Date | Yes |     |     |
| reason | Small Text | Yes |     |     |
| supporting_reference | Data | No  | Payment/disbursement/etc |     |
| status | Select | Yes | Draft / Submitted / Approved / Rejected / Posted / Cancelled |     |
| requested_by | Link(User) | Yes |     |     |
| approved_by | Link(User) | No  |     |     |
| posted_by | Link(User) | No  |     |     |
| posted_on | Datetime | No  |     |     |

**Status Enum**

Draft  
Submitted  
Approved  
Rejected  
Posted  
Cancelled

**Constraints**

validate():  
if amount <= 0:  
frappe.throw("Adjustment amount must be greater than zero")  
if not reason:  
frappe.throw("Reason is required")

**F. DocType: Chama Statement Snapshot**

**Purpose**

Stores generated statement summary for an entity and period so outputs remain stable and auditable.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| financial_period | Link(Chama Financial Period) | Yes |
| statement_type | Select | Yes |
| entity_type | Select | Yes |
| entity_reference | Dynamic Link | No  |
| generated_on | Datetime | Yes |
| generated_by | Link(User) | Yes |
| summary_json | JSON / Long Text | Yes |
| file_attachment | Attach | No  |

**Statement Types**

- Member Statement
- Chama Financial Statement
- Cash Position Statement
- Reconciliation Summary
- Loan Portfolio Summary
- Contribution Summary

**4.4.6 STATE MACHINES (FORMAL)**

**A. Reconciliation Run State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Open | Balanced | Compare complete | System | variance == 0 and no open issues | Mark balanced |
| Open | Discrepancy | Compare complete | System | variance != 0 or issue exists | Create/attach issues |
| Discrepancy | Resolved | All issues resolved | Treasurer/Chair | no open material issue | Update status |
| Balanced / Resolved | Closed | Final approval | Chair/Treasurer | required approvals present | lock reconciliation snapshot |
| Open / Discrepancy | Closed | Force close | Chair/Admin | policy allows with explanation | mandatory close note |

**B. Reconciliation Issue State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Open | Investigating | Assign/start | Treasurer/Reviewer | —   | owner assigned |
| Investigating | Adjusted | Adjustment posted | Treasurer/Approver | valid adjustment | link adjustment |
| Investigating | Explained | Explanation accepted | Reviewer/Chair | no financial posting needed | store explanation |
| Investigating | Rejected | Invalid issue | Reviewer | issue determined false | note required |
| Adjusted / Explained / Rejected | Closed | Close issue | Reviewer | resolution summary present | close timestamp |

**C. Adjustment Entry State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit | Treasurer | reason and amount valid | notify approver |
| Submitted | Approved | Approve | Chair / authorized approver | authority valid | ready to post |
| Submitted | Rejected | Reject | Approver | note optional/required by policy | notify requester |
| Approved | Posted | Post | Treasurer/System | period open or permitted | affect expected balance |
| Draft / Submitted | Cancelled | Cancel | Requester/Admin | not posted | no financial effect |

**D. Financial Period State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Open | Open period | Admin/Treasurer | valid dates | allow postings |
| Open | Closing | Start close | Treasurer | close prep complete | begin final checks |
| Closing | Closed | Close period | Chair/Treasurer | reconciliation complete | lock period |
| Closed | Archived | Archive | Admin | retention policy | readonly |

**4.4.7 EXPECTED BALANCE ENGINE**

**A. Source Inputs**

Expected balance shall be computed from authoritative source events only.

**Inflows**

- contribution payments in status Allocated or Partially Allocated to valid obligations
- loan repayments posted through Lending
- investment returns recorded as inflow events
- approved other inflows
- approved positive adjustments

**Outflows**

- executed disbursements
- loan disbursements mirrored from Lending
- investment outflows
- approved negative adjustments

**Opening Position**

- prior closed period ending balance or configured opening balance

**B. Calculation Pseudocode**

def compute_expected_balance(chama, as_of_datetime):  
opening = get_opening_balance(chama, as_of_datetime)  
<br/>contribution_inflows = get_contribution_inflows(chama, as_of_datetime)  
loan_repayments = get_loan_repayments(chama, as_of_datetime)  
investment_inflows = get_investment_inflows(chama, as_of_datetime)  
other_inflows = get_other_inflows(chama, as_of_datetime)  
<br/>disbursements = get_executed_disbursements(chama, as_of_datetime)  
loan_disbursements = get_loan_disbursements(chama, as_of_datetime)  
investment_outflows = get_investment_outflows(chama, as_of_datetime)  
other_outflows = get_other_outflows(chama, as_of_datetime)  
<br/>adjustments_positive = get_posted_adjustments(chama, as_of_datetime, direction="Increase Balance")  
adjustments_negative = get_posted_adjustments(chama, as_of_datetime, direction="Decrease Balance")  
<br/>return (  
opening  
\+ contribution_inflows  
\+ loan_repayments  
\+ investment_inflows  
\+ other_inflows  
\+ adjustments_positive  
\- disbursements  
\- loan_disbursements  
\- investment_outflows  
\- other_outflows  
\- adjustments_negative  
)

**C. Source-Level Expected Balances**

Where possible, expected balance shall also be computed per source bucket:

- bank
- mobile money
- cash
- other

If source attribution is unavailable for a transaction, it falls into:

- Unassigned Source Bucket

This bucket must be visible and should trend toward zero through operational discipline.

**4.4.8 ACTUAL BALANCE CAPTURE**

**A. Sources**

Actual balances may be captured for:

- each configured bank account
- each configured mobile money wallet
- each configured cashbox
- any other configured holding source

**B. Entry Modes**

| **Mode** | **Description** |
| --- | --- |
| Manual | Treasurer enters amount |
| Statement Import | Uploaded bank/mobile statement summarized into a value |
| API | Future automated pull |

**C. Validation Rules**

- actual balance cannot be blank
- source must belong to Chama
- evidence attachment recommended or required per source/policy
- capture timestamp required

**D. Actual Source Capture Example**

{  
"source_type": "Mobile Money",  
"source_name": "M-Pesa Main Wallet",  
"actual_balance": 125000,  
"input_method": "Manual",  
"evidence_attachment": "wallet_screenshot_2026_04_30.png"  
}

**4.4.9 ACTION DEFINITIONS**

**A. Run Reconciliation**

**Input**

{  
"chama": "CH-0001",  
"reconciliation_date": "2026-04-30T18:00:00",  
"source_balances": \[  
{  
"source_type": "Bank",  
"source_name": "Co-op Main Account",  
"actual_balance": 250000  
},  
{  
"source_type": "Mobile Money",  
"source_name": "M-Pesa Main Wallet",  
"actual_balance": 125000  
},  
{  
"source_type": "Cash",  
"source_name": "Office Cashbox",  
"actual_balance": 15000  
}  
\]  
}

**Process**

1.  calculate expected total and source balances
2.  save actual balances
3.  compute variance
4.  determine initial run status
5.  create issues if mismatch

**Output**

{  
"status": "success",  
"data": {  
"reconciliation_id": "REC-0007",  
"expected_total_balance": 390000,  
"actual_total_balance": 390500,  
"total_variance": 500,  
"status": "Discrepancy",  
"issues_created": 1  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| RC001 | No active financial period or invalid reconciliation date |
| RC002 | Duplicate reconciliation already exists for same snapshot window |
| RC003 | Actual source balance input invalid |

**B. Create Reconciliation Issue**

**Input**

{  
"reconciliation_run": "REC-0007",  
"issue_type": "Unknown",  
"source_type": "Mobile Money",  
"amount": 500,  
"description": "Unexplained excess in wallet balance"  
}

**Process**

- validate run exists
- create issue
- assign owner optionally

**Output**

{  
"status": "success",  
"data": {  
"issue_id": "RCI-0012",  
"status": "Open"  
},  
"errors": \[\]  
}

**C. Submit Adjustment Entry**

**Input**

{  
"chama": "CH-0001",  
"financial_period": "FP-2026-04",  
"reconciliation_issue": "RCI-0012",  
"adjustment_type": "Missing Inflow",  
"direction": "Increase Balance",  
"amount": 500,  
"effective_date": "2026-04-30",  
"reason": "Verified manual deposit not previously captured"  
}

**Process**

- validate open period
- validate issue/status
- create adjustment in Draft/Submitted

**Output**

{  
"status": "success",  
"data": {  
"adjustment_id": "ADJ-0009",  
"status": "Submitted"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| RC101 | Financial period is closed |
| RC102 | Adjustment amount invalid |
| RC103 | Issue already resolved or not eligible |

**D. Post Adjustment**

**Input**

{  
"adjustment_id": "ADJ-0009"  
}

**Process**

- verify Approved
- verify period open
- mark Posted
- affect expected balance calculations
- update issue if linked

**Output**

{  
"status": "success",  
"data": {  
"adjustment_id": "ADJ-0009",  
"status": "Posted"  
},  
"errors": \[\]  
}

**E. Close Financial Period**

**Input**

{  
"financial_period": "FP-2026-04",  
"close_note": "April period closed after reconciliation approval"  
}

**Process**

1.  ensure no blocking open issues
2.  ensure final reconciliation exists
3.  generate statement snapshots
4.  lock period
5.  update status to Closed

**Output**

{  
"status": "success",  
"data": {  
"financial_period": "FP-2026-04",  
"status": "Closed",  
"statement_snapshots_generated": 4  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| RC201 | Open material reconciliation issues remain |
| RC202 | No approved reconciliation available for period |
| RC203 | Period already closed |

**4.4.10 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Reconciliation Dashboard (Desk)**

**Purpose**

Primary operational control surface for treasurer and reviewers.

**Summary Cards**

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| expected_total_balance | Currency | System-computed |
| actual_total_balance | Currency | Sum of entered actuals |
| total_variance | Currency | actual - expected |
| reconciliation_status | Badge | Balanced / Discrepancy / Resolved |
| open_issue_count | Int | Count of unresolved issues |

**Source Balance Grid**

| **Field** | **Type** |
| --- | --- |
| source_type | Select |
| source_name | Data |
| expected_balance | Currency |
| actual_balance | Currency |
| variance | Currency |
| input_method | Select |
| evidence_attachment | Attach |

**Actions**

- Run Reconciliation
- Save Draft Inputs
- Create Issue
- View Issues
- Export Reconciliation Summary

**UI Rules**

- red highlight if variance != 0
- source rows sorted by largest absolute variance first
- attachments previewable where supported

**B. Screen: Reconciliation Issue Detail**

**Fields**

| **Field** | **Type** | **Editable By** |
| --- | --- | --- |
| issue_type | Select | Treasurer |
| source_type | Select | Treasurer |
| amount | Currency | Treasurer |
| description | Text | Treasurer |
| suspected_cause | Text | Treasurer/Reviewer |
| owner_user | Link(User) | Treasurer/Admin |
| status | Select | Reviewer |
| resolution_summary | Text | Reviewer/Chair |

**Actions**

- Assign
- Start Investigation
- Link Adjustment
- Mark Explained
- Close Issue

**C. Screen: Adjustment Entry Form**

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| adjustment_type | Select | Yes |
| direction | Select | Yes |
| amount | Currency | Yes |
| effective_date | Date | Yes |
| reason | Text | Yes |
| reconciliation_issue | Link | No  |
| supporting_reference | Data | No  |

**Actions**

- Save Draft
- Submit
- Approve
- Post
- Cancel

**D. Screen: Financial Statement Viewer**

**Statement Types**

- Member Statement
- Chama Statement
- Cash Position Report
- Reconciliation Summary

**Display Sections**

- period metadata
- opening balance
- inflows
- outflows
- adjustments
- closing balance
- notes / status

**Actions**

- Export PDF
- Export XLSX
- View source transactions
- Compare to prior period

**4.4.11 FINANCIAL STATEMENTS (DETAILED)**

**A. Member Statement**

**Purpose**

Provide a member-specific financial summary for a selected period.

**Inputs**

- contributions due/paid/overdue
- loans and repayments
- benefits/disbursements received
- investment ownership/returns
- penalties and waivers
- final member net position

**Standard Sections**

1.  Member details
2.  Period summary
3.  Contribution breakdown
4.  Loan summary
5.  Disbursement summary
6.  Investment summary
7.  Closing member position

**B. Chama Financial Statement**

**Purpose**

Provide the full group financial picture for a defined period.

**Standard Sections**

1.  Opening position
2.  Total inflows
3.  Total outflows
4.  Loan portfolio summary
5.  Reserve / fund balances
6.  Adjustments
7.  Closing position
8.  Reconciliation status

**C. Cash Position Statement**

**Purpose**

Compare expected and actual holdings by source.

**Standard Sections**

- source balances
- expected per source
- actual per source
- variance per source
- total variance

**D. Reconciliation Summary Statement**

**Purpose**

Provide final evidence for audit and period close.

**Standard Sections**

- reconciliation run metadata
- summary balances
- issues raised
- issues resolved
- adjustments posted
- approvals

**4.4.12 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View own statement | Yes | Yes | Yes | No  | Yes | Yes |
| View Chama statements | No  | Yes | Yes | Limited | Yes | Yes |
| Run reconciliation | No  | Yes | No  | No  | No  | Yes |
| Create issue | No  | Yes | No  | No  | No  | Yes |
| Submit adjustment | No  | Yes | No  | No  | No  | Yes |
| Approve adjustment | No  | Limited | Yes | No  | No  | Yes |
| Post adjustment | No  | Yes | No  | No  | No  | Yes |
| Close period | No  | Limited | Yes | No  | No  | Yes |
| View audit/reconciliation logs | No  | Yes | Yes | No  | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Reconciliation Run | actual_total_balance | No  | Read/Write | Read | Read |
| Issue | suspected_cause | No  | Read/Write | Read | Read |
| Adjustment | approved_by | No  | Read | Write | Read |
| Statement Snapshot | summary_json | Own if member-scoped | Read | Read | Read |

**C. Chama Scope Rule**

All reconciliation runs, issues, adjustments, and statements must be Chama-filtered:

doc.chama == current_user_selected_chama

**4.4.13 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| Reconciliation discrepancy detected | run variance != 0 | Treasurer | App/SMS | reconciliation_discrepancy_detected | High |
| Large variance threshold exceeded | abs(variance) > threshold | Chair/Treasurer | App/SMS | reconciliation_large_variance | High |
| Issue assigned | owner set | Assigned user | App | reconciliation_issue_assigned | Medium |
| Adjustment submitted | submit | Approver | App | adjustment_submitted | Medium |
| Adjustment approved | approve | Treasurer | App | adjustment_approved | Medium |
| Period closed | close period | Chair/Treasurer/Members (summary) | App/Email optional | financial_period_closed | Low/Medium |

**Example Template: reconciliation_discrepancy_detected**

A reconciliation discrepancy of {total_variance} has been detected for {chama_name} on {reconciliation_date}. Review is required.

**Example Template: financial_period_closed**

The financial period {period_name} has been closed. Final statements are now available.

**4.4.14 API ENDPOINTS (FULL)**

**A. Run Reconciliation**

POST /api/method/chama.reconciliation.run

**B. Get Reconciliation Status**

GET /api/method/chama.reconciliation.status?chama=CH-0001&period=FP-2026-04

**C. Create Issue**

POST /api/method/chama.reconciliation.create_issue

**D. Submit Adjustment**

POST /api/method/chama.reconciliation.submit_adjustment

**E. Approve Adjustment**

POST /api/method/chama.reconciliation.approve_adjustment

**F. Post Adjustment**

POST /api/method/chama.reconciliation.post_adjustment

**G. Close Period**

POST /api/method/chama.reconciliation.close_period

**H. Get Statement**

GET /api/method/chama.statement.get?statement_type=CHAMA&period=FP-2026-04&chama=CH-0001

**Example Response**

{  
"status": "success",  
"data": {  
"statement_type": "CHAMA",  
"financial_period": "FP-2026-04",  
"opening_balance": 300000,  
"inflows": 150000,  
"outflows": 60000,  
"adjustments": 500,  
"closing_balance": 390500  
},  
"errors": \[\]  
}

**4.4.15 REPORTS**

**A. Reconciliation Summary Report**

**Columns**

- Reconciliation ID
- Date
- Expected Balance
- Actual Balance
- Variance
- Status
- Reviewer
- Approver

**B. Variance Trend Report**

**Purpose**

Track variance over time by period or source.

**Columns**

- Date / Period
- Source
- Variance
- Resolution Type
- Days to Resolve

**C. Open Issues Report**

**Columns**

- Issue ID
- Type
- Amount
- Source
- Status
- Owner
- Age in Days

**D. Adjustment Register**

**Columns**

- Adjustment ID
- Type
- Direction
- Amount
- Reason
- Status
- Posted By
- Effective Date

**E. Member Statement Report**

**Filters**

- Chama
- Member
- Period
- Date Range

**4.4.16 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Financial Period | Required |
| Custom DocType | Chama Reconciliation Run | Required |
| Child Table | Reconciliation Source Balance | Required |
| Custom DocType | Chama Reconciliation Issue | Required |
| Custom DocType | Chama Adjustment Entry | Required |
| Custom DocType | Chama Statement Snapshot | Required |
| Workflow | Adjustment Approval | Recommended |
| Workflow | Period Close Approval | Recommended |
| Reports | reconciliation / variance / issues / adjustments / statements | Required |
| Scheduler | reminder and status refresh jobs | Required |

**4.4.17 WORKFLOW CONFIGURATION**

**Workflow Name: Adjustment Approval**

| **State** | **Doc Status** | **Allow Edit By** | **Transition Action** |
| --- | --- | --- | --- |
| Draft | 0   | Treasurer | Submit |
| Submitted | 0   | Approver | Approve / Reject |
| Approved | 1-style controlled | Treasurer/System | Post |
| Rejected | final | No edit | End |
| Posted | final | No edit | End |
| Cancelled | final | No edit | End |

**Workflow Name: Financial Period Close**

| **State** | **Meaning** |
| --- | --- |
| Open | transactions active |
| Closing | final controls underway |
| Closed | locked |
| Archived | retention mode |

**4.4.18 SERVER LOGIC / HOOKS**

**A. Run Reconciliation**

def run_reconciliation(chama, reconciliation_date, source_balances):  
expected = compute_expected_balance(chama, reconciliation_date)  
actual = sum(x\["actual_balance"\] for x in source_balances)  
variance = actual - expected  
<br/>run = create_reconciliation_run(  
chama=chama,  
reconciliation_date=reconciliation_date,  
expected_total_balance=expected,  
actual_total_balance=actual,  
total_variance=variance  
)  
<br/>for row in source_balances:  
create_source_balance_row(run, row)  
<br/>if variance == 0:  
run.status = "Balanced"  
else:  
run.status = "Discrepancy"  
auto_create_initial_issue(run, variance)  
<br/>run.save()

**B. Post Adjustment**

def post_adjustment(adjustment):  
ensure_status(adjustment, "Approved")  
ensure_period_open(adjustment.financial_period)  
adjustment.status = "Posted"  
adjustment.posted_on = now()  
adjustment.save()  
if adjustment.reconciliation_issue:  
refresh_issue_resolution(adjustment.reconciliation_issue)

**C. Close Period**

def close_financial_period(period):  
ensure_no_open_blocking_issues(period)  
ensure_final_reconciliation_exists(period)  
generate_statement_snapshots(period)  
period.status = "Closed"  
period.closed_on = now()  
period.save()

**4.4.19 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Missing transaction discovered after close | source comparison/manual discovery | create new-period adjustment or controlled reopen | Yes |
| Duplicate inflow/outflow | duplicate detection / issue review | create issue, reverse or adjust | Yes |
| Backdated adjustment into closed period | effective date in closed period | block or require controlled reopen policy | Yes |
| Negative balance result | expected/actual < 0 where not allowed | alert and block sensitive downstream actions | Yes |
| Multi-source mismatch with correct total | source-level variances offsetting | still create issues per source | Yes |
| Statement regenerated after change | snapshot mismatch | preserve prior snapshot and version new one | Yes |
| Imported statement value differs from manual entry | source duplicate capture | require user selection / supersede trail | Yes |
| Unassigned source bucket non-zero | transactions lacking source | warn and require cleanup | Yes |

**4.4.20 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | contribution payments increase expected balance |
| Loans | repayments increase; loan disbursements decrease expected balance |
| Disbursements | executed payouts reduce expected balance |
| Investments | purchases reduce and returns increase expected balance |
| Budgeting | budget performance reports use actual outflow figures |
| Notifications | discrepancy / large variance / close events feed queue |
| Analytics | risk and liquidity dashboards consume reconciliation outputs |
| Member Lifecycle | member statements aggregate reconciliation-backed transactions |

**4.4.21 CRITICAL IMPLEMENTATION RULES**

- Reconciliation runs must be reproducible from source transactions and stored actual balances
- No financial correction may occur by direct editing of historical transactional records
- Adjustment entries are the only approved path for controlled balance correction outside source-transaction reversal
- Closed periods must be read-only except through explicit reopen or new-period correction policy
- Statement snapshots must preserve what was issued at close time
- Every reconciliation run, issue, and adjustment must include chama
- Source-level variance must remain visible even when total variance nets to zero
- Reconciliation approval must be separate from transaction entry wherever operationally possible

## MODULE 4.5 — NOTIFICATIONS & COMMUNICATION

**4.5.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Event generation | Source modules (Loans, Contributions, Disbursements, Meetings, Voting, Budgeting, Reconciliation, Member Lifecycle, Investments) |
| Notification queue and delivery orchestration | Custom |
| User-facing inbox / read state | Custom |
| Template storage and rendering | Custom + Frappe capabilities |
| Background delivery jobs | Frappe scheduler / background jobs |
| Channel integrations | Custom wrappers around SMS / Email / App notification mechanisms |
| Permissions and tenant scoping | ERPNext/Frappe + custom enforcement |

**4.5.2 MODULE PURPOSE**

The Notifications & Communication module shall manage:

- event-driven notifications
- scheduled reminders
- cross-module operational alerts
- in-app message delivery
- SMS delivery for critical events
- optional email delivery
- notification templates
- recipient targeting
- delivery status tracking
- read/unread tracking
- notification preferences
- deduplication and throttling
- Chama-scoped communication history

This module must explicitly separate:

1.  **Notification Event**  
    the business event that occurred
2.  **Notification Template**  
    the content pattern for rendering a message
3.  **Notification Queue Item**  
    the scheduled delivery job
4.  **Notification Delivery Record**  
    the actual outcome per channel/recipient
5.  **Inbox Item**  
    what the user sees in-app

That separation is mandatory.

**4.5.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall use a hybrid reuse-first model.

**Reuse from ERPNext / Frappe**

- User records
- roles and permissions
- scheduler/background jobs
- Email queue concepts where useful
- standard notification patterns where useful, but not relied on exclusively
- file attachments and links
- doctype list/form UI
- audit/version patterns

**Custom Chama layer**

- event registry
- template engine aligned to Chama events
- per-recipient delivery records
- in-app inbox
- SMS abstraction
- deduplication rules
- reminder schedules
- notification preference model
- cross-Chama scoping
- mobile-friendly retrieval APIs

**Rule**

We shall not rely on built-in Frappe notifications alone as the entire communication system, because this platform requires:

- explicit event traceability
- per-channel delivery control
- delivery retry logic
- recipient-level auditability
- member mobile inbox
- Chama-context rendering

**4.5.4 NOTIFICATION CHANNELS**

The system shall support the following channels in v1/v1.1 architecture:

| **Channel Code** | **Label** | **Status** | **Purpose** |
| --- | --- | --- | --- |
| APP | In-App | Required | Primary member and officer inbox |
| SMS | SMS | Required | Critical reminders and alerts |
| EMAIL | Email | Optional/Configurable | Reports, summaries, optional notices |
| PUSH | Push Notification | Future-ready | Mobile device push if app supports |
| WA_BUS | WhatsApp / Business Message | Future | Optional later expansion |

In v1, APP and SMS must be first-class.

**4.5.5 EVENT CATALOGUE**

The platform shall standardize notification event types.

**A. Contributions Events**

- contribution_due_soon
- contribution_due_today
- contribution_overdue
- contribution_payment_received
- contribution_duplicate_flagged
- contribution_waiver_submitted
- contribution_waiver_approved
- contribution_cycle_generated

**B. Loans Events**

- loan_submitted
- loan_under_review
- loan_guarantor_request
- loan_guarantor_rejected
- loan_approved
- loan_rejected
- loan_ready_for_disbursement
- loan_disbursed
- loan_repayment_due
- loan_overdue
- loan_defaulted
- loan_restructured
- guarantor_liability_triggered

**C. Disbursement Events**

- disbursement_request_submitted
- disbursement_request_escalated
- disbursement_request_approved
- disbursement_request_rejected
- disbursement_ready_for_execution
- disbursement_executed
- disbursement_execution_failed
- disbursement_reversed

**D. Reconciliation Events**

- reconciliation_discrepancy_detected
- reconciliation_large_variance
- reconciliation_issue_assigned
- adjustment_submitted
- adjustment_approved
- financial_period_closed

**E. Governance Events**

- meeting_scheduled
- meeting_updated
- meeting_reminder
- minutes_published
- proposal_created
- voting_open
- vote_closing_soon
- resolution_passed
- resolution_rejected

**F. Member Lifecycle Events**

- member_application_received
- member_approved
- member_rejected
- member_suspended
- member_reactivated
- exit_initiated
- exit_completed

**G. Investment Events**

- investment_proposed
- investment_approved
- investment_rejected
- valuation_updated
- returns_distributed

**H. Platform Events**

- role_changed
- suspicious_activity_detected
- password_or_access_alert
- account_context_switched

**4.5.6 DATA MODEL (FULL)**

**A. DocType: Chama Notification Event**

**Purpose**

Represents the business event that triggered one or more notifications.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Event ID | Data (Auto) | Yes | Example NTE-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| event_type | Event Type | Data | Yes | Must match event catalogue |
| source_module | Source Module | Select | Yes | Contributions / Loans / etc |
| source_doctype | Source DocType | Data | No  |     |
| source_docname | Source Docname | Data | No  |     |
| event_timestamp | Datetime | Yes | Actual event time |     |
| payload_json | JSON / Long Text | Yes | Render variables |     |
| created_by | Link(User) | No  | System or user |     |
| priority | Select | Yes | Low / Medium / High / Critical |     |
| dedupe_key | Data | No  | Optional dedupe support |     |
| status | Select | Yes | Created / Processed / Cancelled |     |

**Status Enum**

Created  
Processed  
Cancelled

**B. DocType: Chama Notification Template**

**Purpose**

Stores renderable message templates by event type and channel.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Template ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | No  | Null means global default |
| event_type | Event Type | Data | Yes |     |
| channel | Channel | Select | Yes | APP / SMS / EMAIL |
| language_code | Data | Yes | Example en, sw |     |
| subject_template | Small Text | No  | For email or rich notifications |     |
| body_template | Long Text | Yes | Jinja-like template |     |
| active | Check | Yes | 1   |     |
| version_no | Int | Yes | Starts at 1 |     |
| is_default | Check | Yes | 0/1 |     |

**Constraint**

At most one active default template per:

- event_type
- channel
- language_code
- chama scope

**C. DocType: Chama Notification Queue**

**Purpose**

Represents one queued delivery task per recipient per channel.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Queue ID | Data (Auto) | Yes | Example NTQ-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| notification_event | Link(Chama Notification Event) | Yes |     |     |
| recipient_user | Link(User) | No  | Optional if recipient has system user |     |
| recipient_member | Link(Chama Member) | No  | Optional member anchor |     |
| recipient_phone | Data | No  | Needed for SMS |     |
| recipient_email | Data | No  | Needed for email |     |
| channel | Select | Yes | APP / SMS / EMAIL |     |
| rendered_subject | Small Text | No  |     |     |
| rendered_body | Long Text | Yes |     |     |
| priority | Select | Yes | Low / Medium / High / Critical |     |
| scheduled_send_at | Datetime | Yes |     |     |
| retry_count | Int | Yes | Default 0 |     |
| status | Select | Yes | Pending / Sending / Sent / Failed / Cancelled / Read |     |
| last_error | Small Text | No  |     |     |
| dedupe_key | Data | No  | Prevent duplicates |     |
| source_link | Data | No  | Deep link / mobile route |     |

**Status Enum**

Pending  
Sending  
Sent  
Failed  
Cancelled  
Read

Note:

- Read only makes sense for APP channel or linked inbox record
- SMS/email remain Sent/Failed

**D. DocType: Chama Notification Inbox**

**Purpose**

Represents the in-app message visible to a user.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Inbox ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | Yes |     |
| recipient_user | Link(User) | Yes |     |     |
| recipient_member | Link(Chama Member) | No  |     |     |
| notification_queue | Link(Chama Notification Queue) | Yes | Source queue item |     |
| title | Data | No  |     |     |
| body | Long Text | Yes |     |     |
| event_type | Data | Yes |     |     |
| source_module | Select | No  |     |     |
| source_doctype | Data | No  |     |     |
| source_docname | Data | No  |     |     |
| source_link | Data | No  | route or URL |     |
| is_read | Check | Yes | 0   |     |
| read_at | Datetime | No  |     |     |
| archived | Check | Yes | 0   |     |
| created_at | Datetime | Yes |     |     |

**E. DocType: Chama Notification Preference**

**Purpose**

Stores recipient-level communication preferences.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Preference ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | Yes |     |
| user | Link(User) | Yes |     |     |
| member | Link(Chama Member) | No  |     |     |
| event_type | Data | Yes |     |     |
| app_enabled | Check | Yes | 1   |     |
| sms_enabled | Check | Yes | 1   |     |
| email_enabled | Check | Yes | 0   |     |
| quiet_hours_start | Time | No  |     |     |
| quiet_hours_end | Time | No  |     |     |
| override_critical | Check | Yes | 1   | critical alerts bypass quiet hours |

**Constraint**

One preference record per:

- chama
- user
- event_type

**F. DocType: Chama Communication Broadcast**

**Purpose**

Handles broad group announcements not tied to a transactional event.

**Fields**

| **Field Name** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| audience_type | Select | Yes |
| title | Data | Yes |
| body | Long Text | Yes |
| channel_set | JSON / MultiSelect concept | Yes |
| scheduled_send_at | Datetime | Yes |
| status | Select | Yes |
| created_by | Link(User) | Yes |

**Status Enum**

Draft  
Scheduled  
Sent  
Cancelled

Audience types:

- All Members
- All Officials
- Specific Role
- Selected Members

**4.5.7 STATE MACHINES (FORMAL)**

**A. Notification Event State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Created | Processed | Queue generation complete | System | templates/recipients resolved | queue items created |
| Created | Cancelled | invalid/no recipients | System/Admin | event unusable | log reason |

**B. Queue Item State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Pending | Sending | worker picks item | System | scheduled_send_at <= now | attempt send |
| Sending | Sent | provider success / inbox create success | System | delivery succeeded | create inbox if APP |
| Sending | Failed | provider/validation error | System | send failed | increment retry |
| Failed | Pending | retry scheduled | System | retry_count < max_retries | reschedule |
| Pending / Failed | Cancelled | admin/system cancellation | Admin/System | dedupe or invalid recipient | stop send |
| Sent | Read | app inbox opened | User/System | APP channel only | set read timestamp |

**C. Inbox State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Unread | Read | open / mark read | User/System | item visible | store read_at |
| Read | Archived | archive action | User | —   | remove from default inbox |
| Unread | Archived | archive action | User | —   | archive without read |

Represented via booleans rather than explicit workflow.

**D. Broadcast State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** |
| --- | --- | --- | --- | --- |
| Draft | Scheduled | schedule | Admin/Secretary | content valid |
| Scheduled | Sent | scheduler executes | System | scheduled_send_at reached |
| Draft / Scheduled | Cancelled | cancel | Admin/Secretary | not yet sent |

**4.5.8 RECIPIENT RESOLUTION ENGINE**

This is one of the most important pieces.

**A. General Rule**

Recipients shall not be hardcoded in modules.  
Source modules emit events. Notification engine resolves recipients based on:

- event type
- Chama
- source document
- roles
- members involved
- preferences

**B. Recipient Resolution Examples**

| **Event Type** | **Recipient Logic** |
| --- | --- |
| contribution_due_soon | member on obligation |
| loan_submitted | treasurer(s) of same Chama |
| loan_guarantor_request | guarantor member(s) |
| disbursement_ready_for_execution | treasurer / executor role |
| meeting_scheduled | all Active members in Chama |
| vote_closing_soon | all eligible voters who have not voted |
| reconciliation_large_variance | treasurer + chair |

**C. Pseudocode**

def resolve_recipients(event):  
if event.event_type == "contribution_due_soon":  
return \[get_member_user(event.payload_json\["member"\])\]  
if event.event_type == "loan_submitted":  
return get_users_by_role(event.chama, "Treasurer")  
if event.event_type == "meeting_scheduled":  
return get_active_member_users(event.chama)

**4.5.9 TEMPLATE RENDERING ENGINE**

**A. Render Variables**

Templates may use placeholders from payload_json, such as:

- member_name
- chama_name
- amount_due
- due_date
- loan_amount
- meeting_date
- variance_amount

**B. Example APP Template**

**Event: loan_approved**

Subject:

Loan Approved

Body:

Your loan of {amount} has been approved for {chama_name}. Open the app to view the repayment schedule.

**C. Example SMS Template**

**Event: contribution_overdue**

{chama_name}: Your {category_name} contribution of {amount_outstanding} is overdue. Pay as soon as possible to avoid penalties.

**D. Rendering Rules**

- if Chama-specific template exists and active, use it
- else use global default
- if variable missing, fail template render and log error
- rendered body must be saved with queue item for audit

**4.5.10 SCHEDULING, THROTTLING, AND DEDUPLICATION**

**A. Scheduling Rules**

Notifications may be:

- immediate
- delayed
- reminder-based
- scheduled broadcast

Examples:

- contribution_due_soon → 1 day before due date
- meeting_reminder → 24 hours before meeting, optionally 1 hour before
- vote_closing_soon → 24 hours before deadline

**B. Deduplication**

System shall prevent duplicate sends using a dedupe key built from:

{chama}:{event_type}:{recipient}:{source_docname}:{time_bucket}

**C. Throttling**

To avoid spam:

- same low-priority event should not be resent to same user within configured window
- critical alerts may bypass throttling if materially distinct
- batched summaries may replace repeated non-critical notifications

**D. Quiet Hours**

If configured:

- non-critical notifications defer until quiet hours end
- critical events bypass if override_critical = 1

**4.5.11 ACTION DEFINITIONS**

**A. Create Notification Event**

**Input**

{  
"chama": "CH-0001",  
"event_type": "contribution_due_soon",  
"source_module": "Contributions",  
"source_doctype": "Chama Contribution Obligation",  
"source_docname": "COB-0001",  
"payload_json": {  
"member": "MB-0001",  
"member_name": "John Doe",  
"amount_due": 5000,  
"category_name": "Shares",  
"due_date": "2026-05-05",  
"chama_name": "Umoja Chama"  
},  
"priority": "Medium"  
}

**Process**

1.  validate event type
2.  create event record
3.  resolve recipients
4.  resolve channels/preferences
5.  render templates
6.  create queue items
7.  mark event Processed

**Output**

{  
"status": "success",  
"data": {  
"event_id": "NTE-0021",  
"queue_items_created": 2  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| NT001 | Invalid event type |
| NT002 | No template available |
| NT003 | No valid recipients resolved |
| NT004 | Template rendering failed |

**B. Process Notification Queue**

**Trigger**

Background worker / scheduler

**Process**

- fetch Pending items due now
- move item to Sending
- send via channel adapter
- update Sent or Failed
- create inbox item for APP if successful

**Output**

Operational job log rather than direct user response

**C. Mark Inbox Item Read**

**Input**

{  
"inbox_id": "NTI-0041"  
}

**Output**

{  
"status": "success",  
"data": {  
"inbox_id": "NTI-0041",  
"is_read": true,  
"read_at": "2026-05-04T10:11:00"  
},  
"errors": \[\]  
}

**D. Update Notification Preferences**

**Input**

{  
"chama": "CH-0001",  
"event_type": "contribution_due_soon",  
"app_enabled": true,  
"sms_enabled": true,  
"email_enabled": false,  
"quiet_hours_start": "22:00:00",  
"quiet_hours_end": "06:00:00"  
}

**Output**

{  
"status": "success",  
"data": {  
"preference_id": "NTP-0007"  
},  
"errors": \[\]  
}

**E. Create Broadcast**

**Input**

{  
"chama": "CH-0001",  
"audience_type": "All Members",  
"title": "Monthly Meeting Reminder",  
"body": "The monthly meeting will take place on Saturday at 2 PM.",  
"channel_set": \["APP", "SMS"\],  
"scheduled_send_at": "2026-05-07T09:00:00"  
}

**Output**

{  
"status": "success",  
"data": {  
"broadcast_id": "BC-0003",  
"status": "Scheduled"  
},  
"errors": \[\]  
}

**4.5.12 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Notification Inbox (Mobile)**

**Purpose**

Primary user-facing inbox for app-delivered communications.

**List Fields**

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| title | Data | notification title |
| preview_body | Data | truncated body |
| event_type | Badge | notification category |
| created_at | Datetime | delivery time |
| is_read | Icon/flag | read state |
| priority | Badge | Low/Med/High/Critical |

**Detail Fields**

| **Field** | **Type** |
| --- | --- |
| title | Data |
| body | Long Text |
| source_link | Route button |
| created_at | Datetime |
| chama | Link |
| event_type | Data |

**Actions**

- Mark Read
- Open Linked Record
- Archive
- Delete from view (archive only; no hard delete)

**B. Screen: Notification Settings (Mobile/Web)**

**Fields**

| **Field** | **Type** | **Req** | **Notes** |
| --- | --- | --- | --- |
| event_type | Select/Data | Yes | one row per event type |
| app_enabled | Check | Yes |     |
| sms_enabled | Check | Yes |     |
| email_enabled | Check | Yes |     |
| quiet_hours_start | Time | No  |     |
| quiet_hours_end | Time | No  |     |
| override_critical | Check | Yes | default true |

**Behavior**

- if user disables SMS for low-priority events, critical may still send if override_critical enabled
- settings scoped by Chama

**C. Screen: Notification Template Manager (Desk)**

**Fields**

| **Field** | **Type** |
| --- | --- |
| event_type | Data |
| channel | Select |
| language_code | Data |
| subject_template | Text |
| body_template | Long Text |
| active | Check |
| is_default | Check |

**Actions**

- Save Draft
- Test Render
- Activate
- Deactivate
- Clone Template

**Test Render**

Allows sample payload JSON to preview final output.

**D. Screen: Notification Operations Dashboard (Desk)**

**Metrics**

- pending queue count
- failed queue count
- sent today count
- read rate for app notifications
- top failing event types

**Grids**

- recent failed deliveries
- queue backlog
- critical unsent items

**Actions**

- retry failed
- cancel queued
- inspect payload
- inspect template render

**4.5.13 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View own inbox | Yes | Yes | Yes | Yes | Yes | Yes |
| Update own preferences | Yes | Yes | Yes | Yes | Yes | Yes |
| Create broadcast | No  | Limited | Limited | Yes | No  | Yes |
| Manage templates | No  | No  | No  | No  | No  | Yes |
| View notification operations dashboard | No  | Yes | Yes | No  | Yes | Yes |
| Retry failed deliveries | No  | No  | No  | No  | No  | Yes |
| Inspect all queue records | No  | Limited operational | Limited | No  | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- |
| Queue | recipient_phone | No  | Read if operational need | Read | Read/Write |
| Template | body_template | No  | No  | Read | Write |
| Inbox | body | Read own | Read own | No global unless explicit | Read if admin-support allowed |
| Preference | sms_enabled | Write own | Write own | No  | Write |

**C. Chama Scope Rule**

All templates, preferences, events, queue items, and inbox items must be Chama-filtered:

doc.chama == current_user_selected_chama

Global templates may exist with null Chama but are only editable by platform/system admin.

**4.5.14 NOTIFICATION MATRIX (IMPLEMENTATION VIEW)**

Below is the implementation-oriented mapping, not just conceptual examples.

| **Event Type** | **Source Module** | **Recipient Resolver** | **Default Channels** | **Priority** | **Requires Link** |
| --- | --- | --- | --- | --- | --- |
| contribution_due_soon | Contributions | obligation.member | APP, SMS | Medium | Yes |
| contribution_overdue | Contributions | obligation.member | APP, SMS | High | Yes |
| contribution_payment_received | Contributions | payment.member | APP | Medium | Yes |
| loan_submitted | Loans | Chama treasurer(s) | APP, SMS | Medium | Yes |
| loan_guarantor_request | Loans | guarantor member | APP, SMS | High | Yes |
| loan_approved | Loans | borrower | APP, SMS | High | Yes |
| loan_overdue | Loans | borrower + guarantors + treasurer | APP, SMS | High | Yes |
| disbursement_request_submitted | Disbursements | reviewer role | APP | Medium | Yes |
| disbursement_executed | Disbursements | beneficiary | APP, SMS | High | Yes |
| reconciliation_large_variance | Reconciliation | chair + treasurer | APP, SMS | Critical | Yes |
| meeting_scheduled | Meetings | all active members | APP, SMS | Medium | Yes |
| vote_closing_soon | Voting | eligible non-voters | APP | Medium | Yes |
| financial_period_closed | Reconciliation | treasurer/chair/members summary | APP, EMAIL optional | Low | Optional |
| member_suspended | Member Lifecycle | affected member + chair + treasurer | APP, SMS | High | Yes |
| valuation_updated | Investment | all members or investor subset | APP | Medium | Yes |

**4.5.15 CHANNEL ADAPTERS**

The notification engine shall abstract each channel through adapters.

**A. APP Adapter**

- create inbox item
- mark queue Sent if inbox saved
- source_link stored for deep navigation

**B. SMS Adapter**

- validate phone format
- render body to SMS-safe length rules
- send via configured provider
- store provider message ID if available

**C. EMAIL Adapter**

- validate email
- render subject/body
- enqueue/send via configured email pipeline
- store send result

**Interface Pseudocode**

class NotificationChannelAdapter:  
def send(self, queue_item):  
raise NotImplementedError

**4.5.16 BACKGROUND JOBS / SCHEDULERS**

| **Job** | **Frequency** | **Purpose** |
| --- | --- | --- |
| process_notification_queue | Every minute | Send pending notifications |
| retry_failed_notifications | Every 10 minutes | Retry failed sends |
| generate_due_reminders | Daily / scheduled | Create due reminder events |
| generate_meeting_reminders | Hourly | Queue upcoming meeting reminders |
| purge_or_archive_old_inbox | Daily | Archive according to retention rules |
| queue_vote_closing_reminders | Hourly | Remind non-voters |

**Idempotency Rule**

Background jobs must be idempotent. Re-running should not create duplicate queue items if dedupe keys match.

**4.5.17 API ENDPOINTS (FULL)**

**A. Get Inbox**

GET /api/method/chama.notification.inbox

**Query Params**

- chama
- unread_only (optional)
- archived (optional)
- page
- page_size

**Response**

{  
"status": "success",  
"data": {  
"items": \[  
{  
"inbox_id": "NTI-0041",  
"title": "Contribution Due",  
"body": "Reminder: Your Shares contribution of 5000 is due tomorrow.",  
"event_type": "contribution_due_soon",  
"created_at": "2026-05-04T08:00:00",  
"is_read": false,  
"source_link": "/app/contributions/COB-0001"  
}  
\],  
"page": 1,  
"page_size": 20  
},  
"errors": \[\]  
}

**B. Mark Read**

POST /api/method/chama.notification.mark_read

**Request**

{  
"inbox_id": "NTI-0041"  
}

**C. Update Preferences**

POST /api/method/chama.notification.update_preferences

**D. Create Broadcast**

POST /api/method/chama.notification.create_broadcast

**E. Retry Failed Queue Item**

POST /api/method/chama.notification.retry_failed

**Authorization**

Admin only

**F. Test Render Template**

POST /api/method/chama.notification.test_render

**Request**

{  
"template_id": "NTT-0004",  
"sample_payload": {  
"member_name": "John Doe",  
"amount_due": 5000,  
"due_date": "2026-05-05",  
"chama_name": "Umoja Chama"  
}  
}

**4.5.18 REPORTS**

**A. Report: Notification Delivery Register**

**Columns**

- Queue ID
- Event Type
- Recipient
- Channel
- Scheduled At
- Status
- Retry Count
- Last Error

**B. Report: Failed Notifications Report**

**Purpose**

Operations review of repeated failures.

**Columns**

- Queue ID
- Event Type
- Recipient
- Channel
- Failure Reason
- Retry Count
- Last Attempt

**C. Report: Inbox Engagement Report**

**Metrics**

- read rate
- unread backlog
- average time to read
- most common event types

**D. Broadcast Register**

**Columns**

- Broadcast ID
- Audience Type
- Scheduled At
- Sent At
- Status
- Channels

**4.5.19 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Notification Event | Required |
| Custom DocType | Chama Notification Template | Required |
| Custom DocType | Chama Notification Queue | Required |
| Custom DocType | Chama Notification Inbox | Required |
| Custom DocType | Chama Notification Preference | Required |
| Custom DocType | Chama Communication Broadcast | Required |
| Scheduler | process_notification_queue | Required |
| Scheduler | retry_failed_notifications | Required |
| Scheduler | reminder generators | Required |
| Report | Delivery Register | Required |
| Report | Failed Notifications | Required |
| Report | Inbox Engagement | Optional but recommended |
| Desk Page/Workspace | Notification Ops Dashboard | Recommended |

**4.5.20 SERVER LOGIC / HOOKS**

**A. Create Event and Queue**

def create_notification_event(chama, event_type, source_module, payload_json, priority="Medium"):  
event = frappe.get_doc({  
"doctype": "Chama Notification Event",  
"chama": chama,  
"event_type": event_type,  
"source_module": source_module,  
"payload_json": frappe.as_json(payload_json),  
"priority": priority,  
"status": "Created"  
}).insert()  
<br/>recipients = resolve_recipients(event)  
queue_items = build_queue_items(event, recipients)  
event.status = "Processed"  
event.save()  
<br/>return event, queue_items

**B. Process Queue**

def process_notification_queue():  
items = get_due_pending_queue_items()  
for item in items:  
try:  
item.status = "Sending"  
item.save()  
send_via_adapter(item)  
item.status = "Sent"  
item.last_error = None  
item.save()  
if item.channel == "APP":  
create_inbox_item(item)  
except Exception as e:  
item.status = "Failed"  
item.retry_count += 1  
item.last_error = str(e)  
item.save()

**C. Mark Read**

def mark_notification_read(inbox_id, user):  
inbox = frappe.get_doc("Chama Notification Inbox", inbox_id)  
validate_owner(inbox, user)  
inbox.is_read = 1  
inbox.read_at = now()  
inbox.save()

**D. Broadcast Send**

def execute_broadcast(broadcast):  
recipients = resolve_broadcast_audience(broadcast)  
for recipient in recipients:  
create_queue_from_broadcast(broadcast, recipient)  
broadcast.status = "Sent"  
broadcast.save()

**4.5.21 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| SMS failure | provider error | retry within limits, log failure | Yes |
| Duplicate queue creation | dedupe key collision | skip duplicate, log info | Yes |
| Missing phone/email | recipient contact absent | send APP only if possible, log channel failure | Yes |
| Quiet hours active | current time in quiet window | defer non-critical send | Yes |
| Event has no recipients | recipient resolver empty | mark event cancelled or logged as no-op | Yes |
| Template variable missing | render exception | fail queue item, alert admin for template issue | Yes |
| User in multiple Chamas | user context mismatch | only send within event Chama | Yes |
| Massive meeting broadcast | recipient volume high | batch queue creation, paginate processing | Yes |
| Read sync issue on mobile | stale client state | server read timestamp is authoritative | Yes |

**4.5.22 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | due/overdue/payment events emitted |
| Loans | lifecycle and risk events emitted |
| Disbursements | approval/execution/failure events emitted |
| Reconciliation | discrepancy and close events emitted |
| Meetings | schedule/reminder/minutes events emitted |
| Voting | proposal/reminder/result events emitted |
| Member Lifecycle | membership and status change events emitted |
| Investments | proposal/value/returns events emitted |
| Analytics | notification engagement can be measured |
| Multi-Chama | all delivery must remain tenant-scoped |

**4.5.23 CRITICAL IMPLEMENTATION RULES**

- Every notification record must include chama
- Source modules must emit events, not directly send messages
- Rendered notification body must be stored for audit
- APP inbox and SMS/email delivery must have separate delivery records
- Critical notifications may bypass quiet hours only if configured
- Queue processing must be idempotent and deduplicated
- Template changes affect future sends only, not already-rendered queue items
- No module may assume message delivery without checking delivery status
- Communication history must be reviewable per member and per Chama

## MODULE 4.6 — MEETINGS

**4.6.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Meeting master record | Custom |
| Agenda management | Custom |
| Attendance capture | Custom |
| Minutes and attachments | Custom |
| Notifications/reminders | Shared notification engine |
| Linked proposals/resolutions | Voting & Resolutions module |
| Permissions and Chama scoping | ERPNext/Frappe + custom enforcement |
| Reporting | ERPNext reports + custom logic |

**4.6.2 MODULE PURPOSE**

The Meetings module shall manage:

- scheduling of routine and ad hoc meetings
- meeting metadata
- agenda item definition and ordering
- attendance capture
- quorum validation
- minute-taking
- attachment of supporting documents
- linkage to decisions, votes, budgets, loans, and disbursement requests
- meeting closure and publication
- immutable governance history after closure

This module must explicitly separate:

1.  **Meeting**  
    the scheduled governance event
2.  **Agenda Item**  
    a topic or decision item inside the meeting
3.  **Attendance Record**  
    a member’s participation status for the meeting
4.  **Minutes Record**  
    the written official record of discussion and outcome
5.  **Resolution Linkage**  
    downstream decision references created through Voting/Resolution flows

That separation is mandatory.

**4.6.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall be primarily custom, built on top of Frappe/ERPNext framework constructs.

**Reuse from ERPNext / Frappe**

- users, roles, permissions
- DocType forms/lists
- child tables
- attachments
- workflow where approval/publication is needed
- reports
- calendar views where useful
- scheduler and notifications
- audit/version patterns

**Custom Chama layer**

- meeting object model
- quorum logic
- attendance engine
- agenda linking to Chama modules
- minutes capture and publication workflow
- meeting closure controls
- member mobile meeting visibility
- Chama-specific governance reporting

**Rule**

This module shall not rely on generic calendar/event records alone.  
A Chama meeting is a governance record, not just a date/time event.

**4.6.4 MEETING TYPES**

The system shall support normalized meeting types:

| **Type Code** | **Label** | **Description** |
| --- | --- | --- |
| REGULAR | Regular Meeting | Routine scheduled group meeting |
| ADHOC | Ad Hoc Meeting | Special non-routine meeting |
| EMERGENCY | Emergency Meeting | Urgent issue requiring immediate attention |
| COMMITTEE | Committee Meeting | Limited-role governance meeting |
| BOARD | Board / Officials Meeting | Officer-level strategic meeting |
| BUDGET | Budget Review Meeting | Budget-focused session |
| WELFARE | Welfare Committee Meeting | Support and welfare decisions |
| CLOSING | Period Close Meeting | Financial close/review session |

**4.6.5 DATA MODEL (FULL)**

**A. DocType: Chama Meeting**

**Purpose**

Represents a formal scheduled governance event.

**DocType Type**

- Custom DocType
- Is Submittable: Yes
- Workflow Enabled: Yes

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Meeting ID | Data (Auto) | Yes | Example MTG-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| title | Title | Data | Yes | Human-readable meeting title |
| meeting_type | Meeting Type | Select | Yes | Enum from meeting types |
| meeting_date | Meeting Date | Date | Yes |     |
| start_time | Start Time | Time | Yes |     |
| end_time | End Time | Time | No  |     |
| location_type | Location Type | Select | Yes | Physical / Virtual / Hybrid |
| location_text | Location | Data | No  | Venue or call details |
| meeting_status | Status | Select | Yes | Draft / Scheduled / In Progress / Completed / Closed / Cancelled |
| convener | Convener | Link(User) | Yes | Typically Secretary/Chair |
| chairperson_member | Chairperson | Link(Chama Member) | No  | person presiding |
| secretary_member | Secretary | Link(Chama Member) | No  | person recording |
| quorum_required_count | Quorum Required Count | Int | No  | optional hard number |
| quorum_required_percent | Quorum Required % | Percent | No  | optional percentage |
| quorum_basis | Quorum Basis | Select | Yes | Count / Percent / None |
| expected_attendees_count | Expected Attendees Count | Int | No  | derived or manual |
| actual_attendees_count | Actual Attendees Count | Int | No  | computed |
| quorum_achieved | Quorum Achieved | Check | Yes | 0/1 |
| purpose_summary | Purpose Summary | Small Text | No  |     |
| related_period | Link(Chama Financial Period) | No  | for close/budget/review meetings |     |
| published_minutes | Check | Yes | 0   | whether minutes are released |
| minutes_published_at | Datetime | No  |     |     |
| closure_note | Small Text | No  |     |     |
| cancelled_reason | Small Text | No  | if cancelled |     |
| created_by | Link(User) | Yes |     |     |
| created_on | Datetime | Yes |     |     |

**Status Enum**

Draft  
Scheduled  
In Progress  
Completed  
Closed  
Cancelled

**Constraints**

validate():  
if end_time and end_time <= start_time:  
frappe.throw("End Time must be later than Start Time")  
if quorum_basis == "Count" and (quorum_required_count is None or quorum_required_count <= 0):  
frappe.throw("Quorum Required Count is mandatory when quorum basis is Count")  
if quorum_basis == "Percent" and (quorum_required_percent is None or quorum_required_percent <= 0):  
frappe.throw("Quorum Required % is mandatory when quorum basis is Percent")

**B. Child Table: Chama Meeting Agenda Item**

**Parent**

Chama Meeting

**Purpose**

Represents an ordered discussion or decision topic.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| idx | Order | Int | Yes | child row order |
| item_title | Item Title | Data | Yes |     |
| item_description | Description | Small Text | No  |     |
| item_type | Item Type | Select | Yes | Informational / Discussion / Approval / Voting / Review |
| related_module | Related Module | Select | No  | Loans / Disbursements / Budget / Investment / Member / Other |
| related_doctype | Related DocType | Data | No  |     |
| related_docname | Related Docname | Data | No  |     |
| owner_member | Owner Member | Link(Chama Member) | No  |     |
| requires_resolution | Check | Yes | 0/1 |     |
| requires_vote | Check | Yes | 0/1 |     |
| notes | Small Text | No  |     |     |

**C. Child Table: Chama Meeting Attendance**

**Parent**

Chama Meeting

**Purpose**

Captures attendance status by member.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| member | Member | Link(Chama Member) | Yes |     |
| attendance_status | Select | Yes | Present / Absent / Excused / Late |     |
| check_in_time | Datetime | No  |     |     |
| recorded_by | Link(User) | No  |     |     |
| remarks | Small Text | No  |     |     |

**Rule**

Each member may appear only once per meeting.

**D. DocType: Chama Meeting Minutes**

**Purpose**

Stores official minutes separately from the meeting header for control and publication workflow.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Minutes ID | Data (Auto) | Yes | Example MIN-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| meeting | Link(Chama Meeting) | Yes | one-to-one or one primary minutes record |     |
| minutes_status | Select | Yes | Draft / Submitted / Published / Archived |     |
| prepared_by | Link(User) | Yes |     |     |
| reviewed_by | Link(User) | No  |     |     |
| approved_by | Link(User) | No  |     |     |
| summary_text | Long Text / Rich Text | Yes | official meeting narrative |     |
| decisions_summary | Long Text / Rich Text | No  |     |     |
| action_items_summary | Long Text / Rich Text | No  |     |     |
| attachments | Table or Attach | No  | supporting files |     |
| published_at | Datetime | No  |     |     |
| immutable_after_publish | Check | Yes | 1   |     |

**Status Enum**

Draft  
Submitted  
Published  
Archived

**E. DocType: Chama Meeting Action Item**

**Purpose**

Optional but strongly recommended tracking of actions arising from the meeting.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Action Item ID | Data (Auto) | Yes |
| chama | Chama | Link(Chama) | Yes |
| meeting | Link(Chama Meeting) | Yes |     |
| agenda_item_ref | Data / row identifier | No  |     |
| title | Data | Yes |     |
| description | Small Text | No  |     |
| assigned_to_user | Link(User) | No  |     |
| assigned_to_member | Link(Chama Member) | No  |     |
| due_date | Date | No  |     |
| status | Select | Yes |     |
| completion_note | Small Text | No  |     |

**Status Enum**

Open  
In Progress  
Completed  
Cancelled  
Overdue

**4.6.6 STATE MACHINES (FORMAL)**

**A. Meeting State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Scheduled | Schedule | Secretary/Chair/Admin | required fields valid | notify attendees |
| Scheduled | In Progress | Start meeting | Secretary/Chair | meeting date/time valid or manual override | open attendance/minutes entry |
| In Progress | Completed | End meeting | Secretary/Chair | attendance captured, minutes draft present | freeze attendance by default |
| Completed | Closed | Close meeting | Chair/Secretary | quorum assessed, minutes submitted, action items created | notify publication path |
| Draft / Scheduled | Cancelled | Cancel | Secretary/Chair/Admin | reason required | notify attendees |

**B. Minutes State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit minutes | Secretary | summary_text present | notify reviewer |
| Submitted | Published | Publish | Chair/Secretary/Approver | meeting completed/closed | release to member view |
| Submitted | Draft | Return for edit | Reviewer | reason optional/required by policy | unlock edits |
| Published | Archived | Archive | Admin | retention process | readonly |

**C. Action Item State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** |
| --- | --- | --- | --- | --- |
| Open | In Progress | Accept/start | Assignee | —   |
| Open / In Progress | Completed | Complete | Assignee/Reviewer | completion note optional |
| Open / In Progress | Cancelled | Cancel | Secretary/Chair | reason recommended |
| Open / In Progress | Overdue | Scheduler | due_date < today and not completed |     |

**4.6.7 QUORUM ENGINE**

Quorum is central to whether decisions are valid.

**A. Quorum Modes**

| **Mode** | **Meaning** |
| --- | --- |
| Count | fixed minimum number |
| Percent | percentage of eligible attendees |
| None | informational meeting, no quorum enforcement |

**B. Eligible Population**

By default, quorum is measured against:

- Active members in the Chama  
    Optionally configurable to:
- Active voting-eligible members only
- specific committee membership

**C. Formula**

**Count-based**

quorum_achieved = actual_present_count >= quorum_required_count

**Percent-based**

quorum_achieved = (actual_present_count / eligible_population_count) \* 100 >= quorum_required_percent

**D. Attendance Count Rules**

- Present counts toward quorum
- Late may count if configured
- Excused and Absent do not count

**E. Side Effects**

- if quorum not achieved:
    - meeting may still proceed for discussion
    - decisions requiring quorum cannot be finalized
    - voting/resolution module must be informed

**4.6.8 ACTION DEFINITIONS**

**A. Create Meeting**

**Input**

{  
"chama": "CH-0001",  
"title": "April General Meeting",  
"meeting_type": "REGULAR",  
"meeting_date": "2026-04-28",  
"start_time": "14:00:00",  
"location_type": "Physical",  
"location_text": "Community Hall",  
"quorum_basis": "Percent",  
"quorum_required_percent": 50  
}

**Process**

1.  validate required fields
2.  create meeting in Draft
3.  optionally auto-populate expected attendees count
4.  if schedule action invoked, move to Scheduled
5.  create notifications

**Output**

{  
"status": "success",  
"data": {  
"meeting_id": "MTG-0004",  
"meeting_status": "Scheduled"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MT001 | Invalid meeting date/time |
| MT002 | Quorum configuration invalid |
| MT003 | Chama is not active |

**B. Add Agenda Item**

**Input**

{  
"meeting": "MTG-0004",  
"item_title": "Review welfare disbursement request DBR-0008",  
"item_type": "Approval",  
"related_module": "Disbursements",  
"related_doctype": "Chama Disbursement Request",  
"related_docname": "DBR-0008",  
"requires_resolution": true,  
"requires_vote": true  
}

**Output**

{  
"status": "success",  
"data": {  
"meeting": "MTG-0004",  
"agenda_count": 4  
},  
"errors": \[\]  
}

**C. Record Attendance**

**Input**

{  
"meeting": "MTG-0004",  
"attendance": \[  
{  
"member": "MB-0001",  
"attendance_status": "Present"  
},  
{  
"member": "MB-0002",  
"attendance_status": "Excused"  
}  
\]  
}

**Process**

- validate members belong to Chama
- upsert attendance rows
- recalc quorum

**Output**

{  
"status": "success",  
"data": {  
"meeting": "MTG-0004",  
"actual_attendees_count": 23,  
"quorum_achieved": true  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MT101 | Duplicate attendance row for member |
| MT102 | Member does not belong to Chama |
| MT103 | Meeting not in attendance-editable state |

**D. Submit Minutes**

**Input**

{  
"meeting": "MTG-0004",  
"summary_text": "The meeting reviewed contributions, welfare requests, and the monthly budget.",  
"decisions_summary": "Members approved welfare request DBR-0008 and deferred investment proposal INV-0002.",  
"action_items_summary": "Treasurer to execute welfare payout by Friday."  
}

**Process**

- create/update minutes record
- validate meeting exists
- validate summary_text present
- move minutes to Submitted if requested

**Output**

{  
"status": "success",  
"data": {  
"minutes_id": "MIN-0004",  
"minutes_status": "Submitted"  
},  
"errors": \[\]  
}

**E. Close Meeting**

**Input**

{  
"meeting": "MTG-0004",  
"closure_note": "Meeting closed after minutes submission and attendance verification."  
}

**Process**

1.  validate meeting In Progress or Completed
2.  ensure attendance exists
3.  ensure minutes draft/submitted exists
4.  compute final quorum state
5.  move meeting to Completed/Closed as configured

**Output**

{  
"status": "success",  
"data": {  
"meeting": "MTG-0004",  
"meeting_status": "Closed",  
"quorum_achieved": true  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MT201 | Meeting cannot be closed without attendance |
| MT202 | Meeting cannot be closed without minutes |
| MT203 | Meeting not in closable state |

**4.6.9 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Meeting List (Desk/Web)**

**Purpose**

List and filter meetings by Chama and state.

**Columns**

- Meeting ID
- Title
- Meeting Type
- Meeting Date
- Status
- Quorum Achieved
- Convener
- Published Minutes

**Filters**

- Chama
- Date range
- Meeting type
- Status
- Quorum achieved

**Actions**

- New Meeting
- Open
- Cancel
- Export list

**B. Screen: Meeting Detail (Desk)**

**Sections**

**1\. Meeting Header**

| **Field** | **Type** |
| --- | --- |
| title | Data |
| meeting_type | Select |
| meeting_date | Date |
| start_time | Time |
| end_time | Time |
| location_type | Select |
| location_text | Data |
| convener | Link(User) |
| chairperson_member | Link(Member) |
| secretary_member | Link(Member) |
| meeting_status | Badge |

**2\. Quorum Panel**

| **Field** | **Type** |
| --- | --- |
| quorum_basis | Select |
| quorum_required_count / percent | Numeric |
| expected_attendees_count | Int |
| actual_attendees_count | Int |
| quorum_achieved | Check/badge |

**3\. Agenda Grid**

- ordered child rows
- create/edit/delete while Draft/Scheduled
- readonly after Completed unless privileged reopen

**4\. Linked Records Panel**

Shows references to:

- proposals
- budgets
- loan exceptions
- disbursement requests
- investment proposals

**5\. Actions**

- Schedule
- Start Meeting
- Record Attendance
- Open Minutes
- Close Meeting
- Publish Minutes
- Cancel Meeting

**C. Screen: Attendance Capture (Desk/Tablet-Friendly)**

**Purpose**

Fast meeting-day capture.

**Fields**

| **Field** | **Type** |
| --- | --- |
| member_name | Data |
| attendance_status | Select |
| check_in_time | Datetime |
| remarks | Small Text |

**Behavior**

- searchable member list
- quick-toggle buttons for Present/Absent/Excused
- save in batch
- quorum counter updates live

**D. Screen: Meeting View (Mobile Member)**

**Purpose**

Member-facing visibility.

**Display**

- upcoming meetings
- title
- date/time
- location
- agenda summary (if visible)
- published minutes links
- attendance status for self (optional if tracked individually)

**Actions**

- View details
- Add to calendar (future)
- View published minutes

Members do not edit meeting records.

**E. Screen: Minutes Editor (Desk)**

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| summary_text | Rich Text / Long Text | Yes |
| decisions_summary | Rich Text / Long Text | No  |
| action_items_summary | Rich Text / Long Text | No  |
| attachments | Attach / child table | No  |

**Actions**

- Save Draft
- Submit
- Publish
- Return for Edit

**Rule**

After publish, content becomes readonly except through controlled archive/version process.

**4.6.10 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View published meetings | Yes | Yes | Yes | Yes | Yes | Yes |
| View unpublished scheduled meetings | Limited if participant/member | Yes | Yes | Yes | Yes | Yes |
| Create meeting | No  | Limited if configured | Yes | Yes | No  | Yes |
| Edit meeting header | No  | No  | Yes | Yes | No  | Yes |
| Manage agenda | No  | No  | Yes | Yes | No  | Yes |
| Record attendance | No  | No  | Limited | Yes | No  | Yes |
| Draft minutes | No  | No  | No  | Yes | No  | Yes |
| Publish minutes | No  | No  | Yes / Secretary if configured | Yes if allowed | No  | Yes |
| Cancel meeting | No  | No  | Yes | Yes | No  | Yes |
| View all meeting audit data | No  | Limited | Yes | Yes | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Secretary** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Meeting | closure_note | No  | Write | Write | Read |
| Meeting | quorum_achieved | Read published result only | Read | Read | Read |
| Minutes | summary_text | Read only if published | Write | Read/Approve | Read |
| Attendance | all rows | No  | Write | Read | Read |

**C. Chama Scope Rule**

All meeting, agenda, attendance, minutes, and action-item records must be Chama-filtered:

doc.chama == current_user_selected_chama

**4.6.11 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| meeting_scheduled | status -> Scheduled | all active members / audience set | APP, SMS | meeting_scheduled | Medium |
| meeting_updated | material detail change | affected attendees | APP | meeting_updated | Medium |
| meeting_reminder | scheduled reminder window | attendees | APP, SMS | meeting_reminder | Medium |
| meeting_cancelled | status -> Cancelled | attendees | APP, SMS | meeting_cancelled | High |
| minutes_submitted | minutes submitted | reviewer/chair | APP | minutes_submitted | Medium |
| minutes_published | minutes published | members | APP | minutes_published | Low/Medium |
| action_item_assigned | action item created | assignee | APP | meeting_action_assigned | Medium |
| action_item_overdue | due date passed | assignee + chair/secretary optional | APP | meeting_action_overdue | Medium |

**Example Template: meeting_scheduled**

A {meeting_type} meeting for {chama_name} has been scheduled on {meeting_date} at {start_time}. Location: {location_text}.

**Example Template: meeting_reminder**

Reminder: {meeting_title} starts on {meeting_date} at {start_time}.

**4.6.12 API ENDPOINTS (FULL)**

**A. Create Meeting**

POST /api/method/chama.meeting.create

**B. Update Meeting**

POST /api/method/chama.meeting.update

**C. Add Agenda Item**

POST /api/method/chama.meeting.add_agenda_item

**D. Record Attendance**

POST /api/method/chama.meeting.record_attendance

**E. Get Meetings**

GET /api/method/chama.meeting.list?chama=CH-0001&status=Scheduled

**F. Get Meeting Detail**

GET /api/method/chama.meeting.detail?meeting=MTG-0004

**G. Submit Minutes**

POST /api/method/chama.meeting.submit_minutes

**H. Publish Minutes**

POST /api/method/chama.meeting.publish_minutes

**I. Close Meeting**

POST /api/method/chama.meeting.close

**Example Response**

{  
"status": "success",  
"data": {  
"meeting_id": "MTG-0004",  
"meeting_status": "Closed",  
"quorum_achieved": true  
},  
"errors": \[\]  
}

**4.6.13 REPORTS**

**A. Report: Meeting Register**

**Columns**

- Meeting ID
- Title
- Type
- Date
- Status
- Quorum Achieved
- Convener
- Minutes Published

**B. Report: Attendance Report**

**Columns**

- Meeting ID
- Member
- Attendance Status
- Check-in Time
- Recorded By

**C. Report: Quorum Compliance Report**

**Purpose**

Track how often meetings achieved quorum.

**Columns**

- Meeting ID
- Date
- Eligible Population
- Actual Present
- Quorum Basis
- Quorum Achieved

**D. Report: Action Item Tracker**

**Columns**

- Action Item ID
- Meeting
- Title
- Assigned To
- Due Date
- Status
- Overdue Flag

**E. Report: Minutes Publication Log**

**Columns**

- Minutes ID
- Meeting
- Prepared By
- Published By
- Published At

**4.6.14 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Meeting | Required |
| Child Table | Chama Meeting Agenda Item | Required |
| Child Table | Chama Meeting Attendance | Required |
| Custom DocType | Chama Meeting Minutes | Required |
| Custom DocType | Chama Meeting Action Item | Recommended |
| Workflow | Meeting lifecycle | Recommended |
| Workflow | Minutes publication | Recommended |
| Reports | register / attendance / quorum / actions / publication | Required |
| Notifications | schedule / reminder / cancel / publish / action item | Required |
| Optional View | calendar view | Recommended |

**4.6.15 WORKFLOW CONFIGURATION**

**Workflow Name: Meeting Lifecycle**

| **State** | **Doc Status** | **Allow Edit By** | **Transition Action** |
| --- | --- | --- | --- |
| Draft | 0   | Secretary/Chair | Schedule |
| Scheduled | 0   | Secretary/Chair | Start / Cancel |
| In Progress | 0   | Secretary/Chair | Complete |
| Completed | 1-style controlled | Secretary/Chair | Close |
| Closed | final | No edit except admin/archive | End |
| Cancelled | final | No edit | End |

**Workflow Name: Minutes Publication**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable by secretary |
| Submitted | reviewer stage |
| Published | released, readonly |
| Archived | retained historical copy |

**4.6.16 SERVER LOGIC / HOOKS**

**A. Recalculate Quorum**

def recalculate_quorum(meeting):  
eligible = get_eligible_attendee_count(meeting)  
present = get_present_count(meeting)  
<br/>if meeting.quorum_basis == "Count":  
achieved = present >= meeting.quorum_required_count  
elif meeting.quorum_basis == "Percent":  
achieved = ((present / eligible) \* 100) >= meeting.quorum_required_percent if eligible else False  
else:  
achieved = True  
<br/>meeting.actual_attendees_count = present  
meeting.quorum_achieved = 1 if achieved else 0  
meeting.save()

**B. On Meeting Schedule**

def on_schedule(meeting):  
notify_meeting_scheduled(meeting)  
queue_meeting_reminders(meeting)

**C. On Minutes Publish**

def publish_minutes(minutes):  
ensure_minutes_publishable(minutes)  
minutes.minutes_status = "Published"  
minutes.published_at = now()  
minutes.save()  
mark_meeting_minutes_published(minutes.meeting)  
notify_minutes_published(minutes.meeting)

**D. Action Item Overdue Check**

def update_meeting_action_items():  
items = get_open_action_items_past_due()  
for item in items:  
item.status = "Overdue"  
item.save()  
notify_action_item_overdue(item)

**4.6.17 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| No quorum but meeting proceeds | quorum false during In Progress/Close | allow discussion, block quorum-dependent decisions | Yes |
| Minutes missing at close time | no minutes record or empty summary | block close | Yes |
| Attendance updated after close | edit attempt | block or require privileged reopen | Yes |
| Same member entered twice | duplicate child row | block save | Yes |
| Meeting cancelled after reminders sent | cancel after Scheduled | send cancellation notices | Yes |
| Minutes edited after publish | save attempt | block unless archive/new version process | Yes |
| Virtual meeting without location | location_type virtual, no link/text | require location_text or meeting link placeholder | Yes |
| Related linked record deleted/cancelled | reference broken | show warning, preserve historical text | Yes |

**4.6.18 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Voting & Resolutions | agenda items may generate proposals/resolutions |
| Disbursements | requests may be reviewed and approved in meetings |
| Budgeting | budgets may be discussed and approved in meetings |
| Loans | exceptions and approvals may be discussed in meetings |
| Notifications | schedules, reminders, publication events emitted |
| Member Lifecycle | active membership defines eligible attendance/quorum population |
| Analytics | meeting frequency, attendance rates, quorum rates become metrics |

**4.6.19 CRITICAL IMPLEMENTATION RULES**

- No formal governance event may be represented only as a notification or note; it must have a Meeting record
- Quorum-dependent decisions must not be finalized if quorum was not achieved
- Minutes must be stored separately from the meeting header to preserve publication workflow and edit control
- Published minutes must be immutable in-place; corrections require controlled versioning or archive/reissue
- Attendance must remain historically reviewable
- Every meeting-related record must include chama
- Meeting closure must require attendance and minutes
- Linked agenda references must not control deletion of related source records or vice versa

## MODULE 4.7 — VOTING & RESOLUTIONS

**4.7.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Proposal master record | Custom |
| Voting configuration and tally logic | Custom |
| Resolution record and enforcement linkage | Custom |
| Meeting linkage | Meetings module |
| Notifications/reminders | Shared notification engine |
| Permissions and Chama scoping | ERPNext/Frappe + custom enforcement |
| Reports | ERPNext reports + custom logic |

**4.7.2 MODULE PURPOSE**

The Voting & Resolutions module shall manage:

- creation of formal proposals
- proposal linkage to meetings and source records
- voter eligibility resolution
- vote capture
- duplicate-vote prevention
- quorum validation for decisions
- vote tallying
- approval / rejection outcomes
- creation of a formal resolution record
- downstream enforcement against linked modules
- immutable governance evidence

This module must explicitly separate:

1.  **Proposal**  
    the matter presented for decision
2.  **Vote Record**  
    one eligible member’s formal response
3.  **Vote Rule Set**  
    the rule used to determine validity and outcome
4.  **Resolution**  
    the official recorded result of the decision
5.  **Enforcement Action**  
    what downstream state or workflow change the result triggers

That separation is mandatory.

**4.7.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall be primarily custom, built on Frappe/ERPNext primitives.

**Reuse from ERPNext / Frappe**

- DocTypes and child tables
- roles and permissions
- reports
- workflows where needed for publication/finalization
- scheduler/background jobs
- attachments
- audit/version patterns

**Custom Chama layer**

- proposal object model
- voter eligibility engine
- quorum engine for proposals
- vote capture and locking
- tally logic
- resolution generation
- downstream enforcement mapping
- member mobile voting experience

**Rule**

This module shall not use informal field flags on source records as a substitute for a formal proposal/resolution record when governance approval is required.

**4.7.4 VOTING TYPES**

The system shall support normalized voting rule types:

| **Type Code** | **Label** | **Description** |
| --- | --- | --- |
| SIMPLE_MAJORITY | Simple Majority | More Yes than No among valid votes cast |
| ABSOLUTE_MAJORITY | Absolute Majority | Yes votes exceed 50% of eligible voters |
| UNANIMOUS | Unanimous | All valid votes cast must be Yes, and optional full participation if configured |
| WEIGHTED_SHARES | Weighted by Shares | Votes weighted by eligible share basis |
| CUSTOM_RULE | Custom Rule | Reserved for future rules engine integration |

**4.7.5 VOTE OPTIONS**

Default options shall be:

| **Option Code** | **Label** |
| --- | --- |
| YES | Yes |
| NO  | No  |
| ABSTAIN | Abstain |

Optional special options may be configured in later phases, but v1 core shall use Yes/No/Abstain.

**4.7.6 DATA MODEL (FULL)**

**A. DocType: Chama Proposal**

**Purpose**

Represents a formal matter for vote.

**DocType Type**

- Custom DocType
- Is Submittable: Yes
- Workflow Enabled: Yes

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Proposal ID | Data (Auto) | Yes | Example PRP-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| title | Title | Data | Yes |     |
| description | Description | Long Text | Yes | proposal narrative |
| proposal_type | Proposal Type | Select | Yes | Loan Exception / Disbursement Approval / Budget Approval / Investment Approval / Member Admission / Member Exit / Policy Change / Other |
| source_module | Source Module | Select | No  | related domain module |
| source_doctype | Source DocType | Data | No  |     |
| source_docname | Source Docname | Data | No  |     |
| meeting | Link(Chama Meeting) | No  | originating meeting if any |     |
| agenda_reference | Data | No  | optional agenda row ref |     |
| voting_type | Select | Yes | from supported voting types |     |
| voting_deadline | Datetime | Yes | final time for voting |     |
| opens_at | Datetime | Yes | voting start time |     |
| proposal_status | Select | Yes | Draft / Open / Closed / Approved / Rejected / Invalid / Cancelled |     |
| quorum_basis | Select | Yes | Count / Percent / None |     |
| quorum_required_count | Int | No  | if count |     |
| quorum_required_percent | Percent | No  | if percent |     |
| eligible_voter_count | Int | No  | computed snapshot |     |
| actual_vote_count | Int | No  | computed |     |
| yes_count | Int | No  | computed |     |
| no_count | Int | No  | computed |     |
| abstain_count | Int | No  | computed |     |
| yes_weight | Float | No  | computed for weighted votes |     |
| no_weight | Float | No  | computed |     |
| abstain_weight | Float | No  | computed |     |
| quorum_achieved | Check | Yes | 0/1 |     |
| result_summary | Small Text | No  | summary line |     |
| created_by | Link(User) | Yes |     |     |
| approved_resolution | Link(Chama Resolution) | No  | created after close |     |
| published_to_members | Check | Yes | 0/1 |     |

**Status Enum**

Draft  
Open  
Closed  
Approved  
Rejected  
Invalid  
Cancelled

**Constraints**

validate():  
if voting_deadline <= opens_at:  
frappe.throw("Voting deadline must be later than opening time")  
if quorum_basis == "Count" and (not quorum_required_count or quorum_required_count <= 0):  
frappe.throw("Quorum count is required")  
if quorum_basis == "Percent" and (not quorum_required_percent or quorum_required_percent <= 0):  
frappe.throw("Quorum percent is required")

**B. Child Table: Proposal Eligible Voter**

**Parent**

Chama Proposal

**Purpose**

Stores the snapshot of who is eligible to vote when the proposal opens.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| member | Member | Link(Chama Member) | Yes |     |
| user | User | Link(User) | No  |     |
| role_at_snapshot | Data | No  | member/official role at vote open |     |
| voting_weight | Float | Yes | default 1.0 |     |
| eligibility_reason | Small Text | No  | why eligible |     |
| has_voted | Check | Yes | 0/1 |     |

**Rule**

Eligibility is snapshotted when proposal opens; later membership changes do not silently alter an already-open vote unless policy explicitly allows recalculation.

**C. DocType: Chama Vote Record**

**Purpose**

Stores one member’s vote for a proposal.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Vote ID | Data (Auto) | Yes | Example VOT-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| proposal | Link(Chama Proposal) | Yes |     |     |
| member | Link(Chama Member) | Yes |     |     |
| user | Link(User) | No  |     |     |
| vote_option | Select | Yes | YES / NO / ABSTAIN |     |
| voting_weight | Float | Yes | copied from eligibility snapshot |     |
| voted_at | Datetime | Yes |     |     |
| voting_channel | Select | Yes | APP / DESK / ASSISTED |     |
| ip_or_device_meta | Small Text | No  | optional audit |     |
| locked | Check | Yes | 1 after save |     |

**Constraints**

validate():  
ensure_member_eligible_for_proposal(self.member, self.proposal)  
enforce_one_vote_per_member_per_proposal()

**D. DocType: Chama Resolution**

**Purpose**

Represents the official outcome after proposal closure.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Resolution ID | Data (Auto) | Yes | Example RES-0001 |
| chama | Chama | Link(Chama) | Yes |     |
| proposal | Link(Chama Proposal) | Yes |     |     |
| resolution_status | Select | Yes | Approved / Rejected / Invalid / Cancelled |     |
| effective_date | Datetime | Yes |     |     |
| quorum_achieved | Check | Yes |     |     |
| vote_summary | Long Text / JSON | Yes | final tally evidence |     |
| decision_text | Long Text | Yes | human-readable decision |     |
| enforcement_status | Select | Yes | Pending / Applied / Failed / Not Applicable |     |
| enforced_on | Datetime | No  |     |     |
| enforced_by | Link(User) | No  | system/user |     |
| enforcement_log | Long Text | No  |     |     |
| published_at | Datetime | No  |     |     |
| published_by | Link(User) | No  |     |     |

**Resolution Status Enum**

Approved  
Rejected  
Invalid  
Cancelled

**Enforcement Status Enum**

Pending  
Applied  
Failed  
Not Applicable

**E. DocType: Chama Vote Rule Set**

**Purpose**

Defines reusable Chama-specific voting logic profiles.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| rule_name | Data | Yes |
| voting_type | Select | Yes |
| quorum_basis | Select | Yes |
| quorum_required_count | Int | No  |
| quorum_required_percent | Percent | No  |
| abstain_affects_denominator | Check | Yes |
| chair_tiebreak_allowed | Check | Yes |
| require_meeting_link | Check | Yes |
| active | Check | Yes |

This allows standardized rules to be reused across proposal types.

**4.7.7 STATE MACHINES (FORMAL)**

**A. Proposal State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Open | Open voting | Secretary/Chair/System | eligible voters resolved, timing valid | create eligibility snapshot, notify voters |
| Open | Closed | Deadline/manual close | System/Chair/Secretary | voting period ended or closure authorized | freeze voting |
| Closed | Approved | Tally result | System | quorum + rule conditions passed | create resolution |
| Closed | Rejected | Tally result | System | quorum passed but support failed | create resolution |
| Closed | Invalid | Tally result | System | quorum failed / invalid conditions | create resolution |
| Draft / Open | Cancelled | Cancel | Chair/Admin | not finalized | notify participants |

**B. Vote Record State Machine**

Vote records do not have a broad editable lifecycle. They are effectively immutable after creation.

| **From** | **To** | **Trigger** | **Actor** | **Conditions** |
| --- | --- | --- | --- | --- |
| New | Locked | Submit vote | Eligible voter | proposal open and no prior vote |
| Locked | Cancelled/Voided (rare) | Admin correction | Admin only | severe exceptional process with audit |

In normal operation, vote updates are not allowed. Corrections require void-and-recast policy if permitted.

**C. Resolution State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Pending generation | Approved / Rejected / Invalid | proposal tally complete | System | —   | save result |
| Approved | Applied | enforcement success | System/Authorized user | downstream action succeeded | update source |
| Approved | Failed | enforcement attempt failed | System/Authorized user | downstream error | alert admins |
| Rejected / Invalid | Not Applicable | finalize | System | no enforcement needed | close loop |

**4.7.8 ELIGIBILITY ENGINE**

This engine determines who is allowed to vote.

**A. Default Eligibility Basis**

Unless overridden by Chama rules:

- Active members only
- Members belonging to the proposal’s Chama
- Members not suspended
- Members with voting rights under constitution

**B. Optional Exclusions**

- Dormant members
- Members in disciplinary suspension
- Members below tenure threshold
- Members with conflict-of-interest restrictions (future / configurable)

**C. Weighted Voting**

If voting_type = WEIGHTED_SHARES, the system shall compute each voter’s weight from a defined basis, such as:

- current share balance
- approved investment weight
- configured proxy weight

**Example Formula**

def resolve_voting_weight(member, proposal):  
if proposal.voting_type == "WEIGHTED_SHARES":  
return get_current_share_balance(member, proposal.chama)  
return 1.0

**Important Rule**

The weight used must be snapshotted into Proposal Eligible Voter when the proposal opens.

**4.7.9 QUORUM AND RESULT ENGINE**

**A. Quorum Calculation**

**Count-based**

quorum_achieved = actual_vote_count >= quorum_required_count

**Percent-based**

quorum_achieved = (actual_vote_count / eligible_voter_count) \* 100 >= quorum_required_percent

actual_vote_count normally includes Yes + No + Abstain, unless the rule set explicitly excludes Abstain.

**B. Result Calculation by Voting Type**

**Simple Majority**

Proposal is Approved if:

yes_count > no_count

**Absolute Majority**

Proposal is Approved if:

yes_count > 50% of eligible_voter_count

**Unanimous**

Proposal is Approved if:

no_count == 0 and yes_count > 0

Optionally, if full participation is required:

yes_count == eligible_voter_count

**Weighted Shares**

Proposal is Approved if:

yes_weight > no_weight

**C. Tie Handling**

If tie occurs:

- if chair_tiebreak_allowed = 1, chair may resolve tie via controlled override action
- otherwise result = Rejected or Re-vote required, according to rule set

**4.7.10 ACTION DEFINITIONS**

**A. Create Proposal**

**Input**

{  
"chama": "CH-0001",  
"title": "Approve welfare disbursement DBR-0008",  
"description": "Members to vote on welfare support request DBR-0008.",  
"proposal_type": "Disbursement Approval",  
"source_module": "Disbursements",  
"source_doctype": "Chama Disbursement Request",  
"source_docname": "DBR-0008",  
"meeting": "MTG-0004",  
"voting_type": "SIMPLE_MAJORITY",  
"opens_at": "2026-04-28T15:00:00",  
"voting_deadline": "2026-04-28T16:00:00",  
"quorum_basis": "Percent",  
"quorum_required_percent": 50  
}

**Process**

1.  validate proposal fields
2.  verify source record if linked
3.  save Draft
4.  on open, snapshot eligible voters

**Output**

{  
"status": "success",  
"data": {  
"proposal_id": "PRP-0007",  
"proposal_status": "Draft"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| VT001 | Voting deadline must be later than open time |
| VT002 | Invalid quorum configuration |
| VT003 | Linked source record not found |

**B. Open Proposal for Voting**

**Input**

{  
"proposal_id": "PRP-0007"  
}

**Process**

- resolve eligible voters
- snapshot weights
- update eligible_voter_count
- move status to Open
- notify voters

**Output**

{  
"status": "success",  
"data": {  
"proposal_id": "PRP-0007",  
"proposal_status": "Open",  
"eligible_voter_count": 34  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| VT101 | Proposal not in openable state |
| VT102 | No eligible voters resolved |
| VT103 | Proposal already open or finalized |

**C. Submit Vote**

**Input**

{  
"proposal_id": "PRP-0007",  
"member": "MB-0001",  
"vote_option": "YES",  
"voting_channel": "APP"  
}

**Process**

1.  validate proposal is Open
2.  validate deadline not passed
3.  validate member eligibility
4.  enforce one vote only
5.  create vote record and lock

**Output**

{  
"status": "success",  
"data": {  
"vote_id": "VOT-0021",  
"proposal_id": "PRP-0007",  
"vote_option": "YES"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| VT201 | Proposal is not open for voting |
| VT202 | Voting deadline has passed |
| VT203 | Member is not eligible to vote |
| VT204 | Vote already exists for this member |

**D. Close and Tally Proposal**

**Input**

{  
"proposal_id": "PRP-0007"  
}

**Process**

1.  freeze voting
2.  count votes
3.  compute quorum
4.  compute result by rule type
5.  create resolution
6.  update proposal status
7.  notify members

**Output**

{  
"status": "success",  
"data": {  
"proposal_id": "PRP-0007",  
"proposal_status": "Approved",  
"resolution_id": "RES-0007",  
"quorum_achieved": true,  
"yes_count": 20,  
"no_count": 10,  
"abstain_count": 2  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| VT301 | Proposal not in closable state |
| VT302 | Tally failed due to invalid vote data |
| VT303 | Proposal already finalized |

**E. Enforce Resolution**

**Input**

{  
"resolution_id": "RES-0007"  
}

**Process**

- inspect linked source module
- apply allowed downstream state change
- update enforcement_status

**Output**

{  
"status": "success",  
"data": {  
"resolution_id": "RES-0007",  
"enforcement_status": "Applied"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| VT401 | Resolution is not approvable for enforcement |
| VT402 | Source module linkage invalid |
| VT403 | Downstream enforcement failed |

**4.7.11 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Proposal List (Desk/Web/Mobile limited)**

**Columns**

- Proposal ID
- Title
- Proposal Type
- Opens At
- Deadline
- Status
- Quorum Achieved
- Linked Module

**Filters**

- Chama
- Proposal Type
- Status
- Date Range
- Meeting

**Actions**

- New Proposal
- Open
- Close
- View Result
- Export

**B. Screen: Proposal Detail (Desk)**

**Sections**

**1\. Proposal Header**

| **Field** | **Type** |
| --- | --- |
| title | Data |
| description | Long Text |
| proposal_type | Select |
| source_module | Select |
| source_doctype | Data |
| source_docname | Data |
| meeting | Link |
| opens_at | Datetime |
| voting_deadline | Datetime |
| proposal_status | Badge |

**2\. Rule Panel**

| **Field** | **Type** |
| --- | --- |
| voting_type | Select |
| quorum_basis | Select |
| quorum_required_count/percent | Numeric |
| eligible_voter_count | Int |
| actual_vote_count | Int |
| quorum_achieved | Check |

**3\. Tally Panel**

| **Field** | **Type** |
| --- | --- |
| yes_count | Int |
| no_count | Int |
| abstain_count | Int |
| yes_weight | Float |
| no_weight | Float |
| abstain_weight | Float |
| result_summary | Small Text |

**4\. Actions**

- Open Voting
- Close Voting
- Generate Resolution
- Enforce Resolution
- Cancel Proposal

**C. Screen: Mobile Voting Screen**

**Purpose**

Simple member-facing vote interface.

**Display**

- proposal title
- proposal description
- voting deadline
- linked context summary (e.g., “Welfare payout request KES 8,000”)
- vote buttons: Yes / No / Abstain

**Actions**

- Submit Vote

**Rules**

- once submitted, vote cannot be edited in normal operation
- show “You have already voted” state if vote exists
- display countdown to deadline if desired

**D. Screen: Resolution Viewer**

**Display**

- proposal reference
- final result
- quorum state
- tally summary
- decision text
- enforcement status
- enforcement log

**Actions**

- View linked source
- Export resolution

**4.7.12 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View open proposals | Yes (eligible/visible) | Yes | Yes | Yes | Yes | Yes |
| Create proposal | No  | Limited if configured | Yes | Yes | No  | Yes |
| Open proposal | No  | No  | Yes | Yes | No  | Yes |
| Submit vote | Yes if eligible | Yes if eligible | Yes if eligible | Yes if eligible | No  | Yes |
| Close/tally proposal | No  | No  | Yes | Yes if configured | No  | Yes |
| Enforce resolution | No  | Limited by source module | Yes | No  | No  | Yes |
| View all vote records | No  | Limited | Yes | Yes | Yes | Yes |
| View own vote record | Yes | Yes | Yes | Yes | No  | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Secretary** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Proposal | description | Read | Write | Write | Read |
| Proposal | result_summary | Read after close | Read/Write via tally | Read | Read |
| Vote Record | vote_option | Read own | Read all if privileged | Read all | Read |
| Resolution | enforcement_status | Read published result | Read | Write/Read | Read |

**C. Secret Ballot Note**

If future requirements include secret ballot:

- member should not see others’ individual votes
- operational users may only see totals
- auditors may need restricted review path  
    For v1, unless otherwise specified, votes are auditable and not fully anonymous.

**D. Chama Scope Rule**

All proposal, vote, rule set, and resolution records must be Chama-filtered:

doc.chama == current_user_selected_chama

**4.7.13 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| proposal_created | proposal opened or made visible | eligible voters | APP, SMS optional | proposal_created | Medium |
| voting_open | status -> Open | eligible voters | APP | voting_open | Medium |
| vote_closing_soon | reminder window | eligible non-voters | APP | vote_closing_soon | Medium |
| proposal_closed | close | proposer/chair/secretary | APP | proposal_closed | Low |
| resolution_passed | result approved | members / affected recipients | APP | resolution_passed | Medium |
| resolution_rejected | result rejected | members / requester | APP | resolution_rejected | Medium |
| enforcement_failed | enforcement failure | chair/admin/treasurer | APP, SMS | resolution_enforcement_failed | High |

**Example Template: voting_open**

Voting is now open for: {proposal_title}. Please cast your vote by {voting_deadline}.

**Example Template: vote_closing_soon**

Reminder: Voting for "{proposal_title}" closes at {voting_deadline}. You have not yet voted.

**4.7.14 API ENDPOINTS (FULL)**

**A. Create Proposal**

POST /api/method/chama.voting.create_proposal

**B. Open Proposal**

POST /api/method/chama.voting.open_proposal

**C. Get Proposal Detail**

GET /api/method/chama.voting.proposal_detail?proposal=PRP-0007

**D. Submit Vote**

POST /api/method/chama.voting.submit_vote

**E. Get My Active Votes**

GET /api/method/chama.voting.my_active_votes?chama=CH-0001

**F. Close Proposal**

POST /api/method/chama.voting.close_proposal

**G. Enforce Resolution**

POST /api/method/chama.voting.enforce_resolution

**H. Resolution Detail**

GET /api/method/chama.voting.resolution_detail?resolution=RES-0007

**Example Response**

{  
"status": "success",  
"data": {  
"proposal_id": "PRP-0007",  
"proposal_status": "Open",  
"title": "Approve welfare disbursement DBR-0008",  
"voting_deadline": "2026-04-28T16:00:00",  
"already_voted": false  
},  
"errors": \[\]  
}

**4.7.15 REPORTS**

**A. Proposal Register**

**Columns**

- Proposal ID
- Title
- Type
- Meeting
- Opens At
- Deadline
- Status
- Quorum Achieved

**B. Vote Participation Report**

**Purpose**

Shows participation rates.

**Columns**

- Proposal ID
- Eligible Voters
- Actual Votes
- Participation %
- Quorum Achieved

**Formula**

participation_rate = actual_vote_count / eligible_voter_count

**C. Resolution Register**

**Columns**

- Resolution ID
- Proposal
- Status
- Effective Date
- Enforcement Status
- Published At

**D. Weighted Vote Summary Report**

**Purpose**

Only for weighted voting scenarios.

**Columns**

- Proposal
- Yes Weight
- No Weight
- Abstain Weight
- Result

**E. Outstanding Enforcement Report**

**Columns**

- Resolution ID
- Proposal
- Approved Date
- Enforcement Status
- Linked Source
- Error / Log

**4.7.16 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Proposal | Required |
| Child Table | Proposal Eligible Voter | Required |
| Custom DocType | Chama Vote Record | Required |
| Custom DocType | Chama Resolution | Required |
| Custom DocType | Chama Vote Rule Set | Recommended |
| Reports | proposals / participation / resolutions / weighted / outstanding enforcement | Required |
| Notifications | open / reminder / result / enforcement failure | Required |
| Scheduler | close overdue proposals, send reminders | Required |
| Optional Workflow | proposal publication/finalization | Recommended |

**4.7.17 SERVER LOGIC / HOOKS**

**A. Open Proposal**

def open_proposal(proposal):  
ensure_openable(proposal)  
eligible = resolve_eligible_voters(proposal)  
if not eligible:  
frappe.throw("No eligible voters resolved")  
<br/>for voter in eligible:  
create_eligible_voter_snapshot(proposal, voter)  
<br/>proposal.eligible_voter_count = len(eligible)  
proposal.proposal_status = "Open"  
proposal.save()  
notify_voting_open(proposal)

**B. Submit Vote**

def submit_vote(proposal, member, vote_option, channel="APP"):  
ensure_proposal_open(proposal)  
ensure_before_deadline(proposal)  
snapshot = get_eligible_snapshot(proposal, member)  
if not snapshot:  
frappe.throw("Member is not eligible to vote")  
if vote_exists(proposal, member):  
frappe.throw("Vote already exists")  
<br/>create_vote_record(  
proposal=proposal,  
member=member,  
vote_option=vote_option,  
voting_weight=snapshot.voting_weight,  
voting_channel=channel  
)  
snapshot.has_voted = 1  
snapshot.save()

**C. Close and Tally Proposal**

def close_proposal(proposal):  
ensure_closable(proposal)  
<br/>tally = calculate_tally(proposal)  
proposal.actual_vote_count = tally\["actual_vote_count"\]  
proposal.yes_count = tally\["yes_count"\]  
proposal.no_count = tally\["no_count"\]  
proposal.abstain_count = tally\["abstain_count"\]  
proposal.yes_weight = tally\["yes_weight"\]  
proposal.no_weight = tally\["no_weight"\]  
proposal.abstain_weight = tally\["abstain_weight"\]  
proposal.quorum_achieved = tally\["quorum_achieved"\]  
<br/>outcome = determine_outcome(proposal, tally)  
proposal.proposal_status = outcome  
proposal.save()  
<br/>resolution = create_resolution_from_proposal(proposal, tally, outcome)  
proposal.approved_resolution = resolution.name  
proposal.save()  
<br/>notify_resolution_result(resolution)

**D. Enforce Resolution**

def enforce_resolution(resolution):  
source = resolve_source_record(resolution.proposal)  
result = apply_resolution_to_source(source, resolution)  
if result\["success"\]:  
resolution.enforcement_status = "Applied"  
else:  
resolution.enforcement_status = "Failed"  
resolution.enforcement_log = result\["error"\]  
resolution.save()

**4.7.18 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Duplicate vote attempt | vote already exists | reject | Yes |
| No quorum | tally calculation | result = Invalid unless rule overrides | Yes |
| Tie in simple majority | yes_count == no_count | tiebreak rule or reject/revote | Yes |
| Deadline passes during vote submit | timestamp check | reject late vote | Yes |
| Member suspended after proposal opens | snapshot vs live change | v1 default: snapshot remains unless admin invalidates | Yes |
| Source record changed materially before resolution enforcement | source mismatch/version check | block enforcement and alert | Yes |
| Proposal cancelled after votes cast | cancel action | preserve records, mark cancelled | Yes |
| Weighted vote data missing | missing share snapshot | block open | Yes |

**4.7.19 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Meetings | proposals often originate from meetings and agenda items |
| Loans | proposal may approve/reject loan exception or special approval |
| Disbursements | proposal may approve payouts |
| Budgeting | budgets may require proposal approval |
| Investments | proposals may approve investments and distributions |
| Member Lifecycle | admissions/exits may require vote |
| Notifications | proposal lifecycle emits events |
| Analytics | participation and governance quality metrics consume proposal/vote data |

**4.7.20 CRITICAL IMPLEMENTATION RULES**

- No governance-required approval may be represented only as a status flag without a Proposal/Resolution trail
- Vote records must be immutable in normal operation after submission
- Eligibility must be snapshotted when proposal opens
- Resolution generation must preserve final tally evidence
- Enforcement must not silently mutate source records without logging
- Every proposal, vote, and resolution record must include chama
- Vote tallies shown to users must exactly match stored vote records
- Proposal closure must freeze further voting
- If quorum is required and not achieved, result must not appear as Approved

## MODULE 4.8 — BUDGETING

**4.8.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Budget master and line items | Custom |
| Budget approval routing | Voting & Resolutions module |
| Budget utilization tracking | Custom |
| Overrun enforcement | Custom |
| Downstream spend linkage | Disbursements module |
| Reporting and dashboards | ERPNext reports + custom logic |
| Permissions and Chama scoping | ERPNext/Frappe + custom enforcement |

**4.8.2 MODULE PURPOSE**

The Budgeting module shall manage:

- creation of budgets for a defined period
- classification of planned allocations
- line-item budgeting
- budget submission for governance approval
- budget activation after approval
- tracking actual spend against line items
- overrun detection and control
- amendment and revision handling
- budget closure and archival
- budget performance reporting

This module must explicitly separate:

1.  **Budget**  
    the financial plan for a period
2.  **Budget Line Item**  
    a category-level planned allocation within the budget
3.  **Budget Approval**  
    the governance path that authorizes the plan
4.  **Budget Utilization**  
    the actual spend recorded against line items
5.  **Budget Amendment**  
    a controlled change to an already created/approved budget

That separation is mandatory.

**4.8.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall be primarily custom, though some conceptual reuse from ERPNext budgeting/accounting ideas is acceptable.

**Reuse from ERPNext / Frappe**

- DocTypes and child tables
- reports and dashboards
- workflows if needed
- roles and permissions
- attachments
- scheduler
- audit/version patterns

**Custom Chama layer**

- Chama-scoped budgets
- budget line item logic
- governance approval linkage
- spend-to-budget linkage
- overrun engine
- amendment/versioning controls
- budget dashboards

**Rule**

Generic ERP budgeting features shall not be assumed sufficient without Chama-specific governance linkage and line-item spend enforcement.

**4.8.4 BUDGET TYPES**

The platform shall support normalized budget types:

| **Type Code** | **Label** | **Description** |
| --- | --- | --- |
| OPERATING | Operating Budget | admin, logistics, routine activities |
| WELFARE | Welfare Budget | emergency and support allocations |
| INVESTMENT | Investment Budget | asset purchase / capital deployment |
| RESERVE | Reserve Budget | planned savings buffer |
| LOAN_POOL | Loan Pool Budget | amount planned for lending availability |
| EVENT | Event Budget | meeting/event/social activity budgets |
| MIXED | Mixed Budget | combination budget across categories |

**4.8.5 DATA MODEL (FULL)**

**A. DocType: Chama Budget**

**Purpose**

Represents a budget for a Chama over a defined period.

**DocType Type**

- Custom DocType
- Is Submittable: Yes
- Workflow Enabled: Yes

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Budget ID | Data (Auto) | Yes | Example BGT-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| budget_name | Budget Name | Data | Yes | Human-readable title |
| budget_type | Budget Type | Select | Yes | Enum from budget types |
| financial_period | Link(Chama Financial Period) | No  | optional if aligned to standard period |     |
| period_start | Date | Yes |     |     |
| period_end | Date | Yes |     |     |
| budget_status | Select | Yes | Draft / Pending Approval / Active / Closed / Rejected / Cancelled |     |
| total_allocated | Currency | Yes | Computed from line items |     |
| total_actual | Currency | Yes | Computed from linked disbursements |     |
| total_remaining | Currency | Yes | total_allocated - total_actual |     |
| total_variance | Currency | Yes | total_actual - total_allocated |     |
| approval_required | Check | Yes | 1/0 |     |
| approval_proposal | Link(Chama Proposal) | No  | generated if governance approval needed |     |
| active_version_no | Int | Yes | version number |     |
| supersedes_budget | Link(Chama Budget) | No  | for amendments/revisions |     |
| overrun_mode | Select | Yes | Block / Warn / Allow With Escalation |     |
| created_by | Link(User) | Yes |     |     |
| approved_by | Link(User) | No  |     |     |
| approved_on | Datetime | No  |     |     |
| closure_note | Small Text | No  |     |     |
| notes | Small Text | No  |     |     |

**Status Enum**

Draft  
Pending Approval  
Active  
Closed  
Rejected  
Cancelled

**Constraints**

validate():  
if period_end < period_start:  
frappe.throw("Budget period end cannot be before period start")

**B. Child Table: Chama Budget Line Item**

**Parent**

Chama Budget

**Purpose**

Represents a category allocation in the budget.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| idx | Order | Int | Yes | row ordering |
| line_code | Line Code | Data | No  | optional code |
| category_name | Category Name | Data | Yes | visible label |
| category_type | Select | Yes | Welfare / Operations / Investment / Loan Pool / Reserve / Event / Other |     |
| description | Small Text | No  |     |     |
| allocated_amount | Currency | Yes | \> 0 |     |
| actual_amount | Currency | Yes | computed from linked disbursements |     |
| remaining_amount | Currency | Yes | allocated - actual |     |
| utilization_percent | Percent | Yes | computed |     |
| overrun_flag | Check | Yes | 0/1 |     |
| linked_source_fund | Data / Select | No  | optional fund affinity |     |
| requires_strict_control | Check | Yes | 0/1 |     |
| notes | Small Text | No  |     |     |

**Computed Rules**

remaining_amount = allocated_amount - actual_amount  
utilization_percent = (actual_amount / allocated_amount) \* 100 if allocated_amount else 0  
overrun_flag = actual_amount > allocated_amount

**C. DocType: Chama Budget Utilization Entry**

**Purpose**

Stores budget-to-disbursement linkage entries.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Utilization ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | Yes |     |
| budget | Link(Chama Budget) | Yes |     |     |
| budget_line_ref | Data / row ref | Yes | line item reference |     |
| linked_disbursement_request | Link(Chama Disbursement Request) | No  |     |     |
| linked_disbursement_execution | Link(Chama Disbursement Execution) | Yes | primary actual source |     |
| amount_utilized | Currency | Yes | \> 0 |     |
| utilization_date | Datetime | Yes |     |     |
| notes | Small Text | No  |     |     |

**Rule**

A utilization entry should only be created from executed disbursements or approved designated actual spend events.

**D. DocType: Chama Budget Amendment**

**Purpose**

Represents a proposed change to an existing budget.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| original_budget | Link(Chama Budget) | Yes |
| amendment_type | Select | Yes |
| reason | Small Text | Yes |
| status | Select | Yes |
| proposed_total_allocated | Currency | No  |
| created_by | Link(User) | Yes |
| proposal_link | Link(Chama Proposal) | No  |
| approved_on | Datetime | No  |

**Amendment Types**

- Line Increase
- Line Decrease
- Reallocation
- New Line Item
- Line Closure
- Full Budget Revision

**Status Enum**

Draft  
Pending Approval  
Approved  
Rejected  
Applied  
Cancelled

**E. Child Table: Chama Budget Amendment Detail**

**Parent**

Chama Budget Amendment

**Purpose**

Specifies line-level changes.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| original_line_ref | Data | No  |
| amendment_action | Select | Yes |
| category_name | Data | Yes |
| old_allocated_amount | Currency | No  |
| new_allocated_amount | Currency | No  |
| delta_amount | Currency | No  |
| notes | Small Text | No  |

**4.8.6 STATE MACHINES (FORMAL)**

**A. Budget State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Pending Approval | Submit | Treasurer/Secretary | line items valid, totals > 0 | create proposal if approval required |
| Draft | Active | Activate directly | Treasurer/Admin | approval not required by config | open budget for utilization |
| Pending Approval | Active | Approval result | System/Chair | linked proposal approved | set approved metadata |
| Pending Approval | Rejected | Approval result | System/Chair | proposal rejected | notify creator |
| Active | Closed | Close budget | Treasurer/Chair | period ended or manual close | lock normal changes |
| Draft / Pending Approval | Cancelled | Cancel | Treasurer/Admin | not active | log cancel |

**B. Budget Amendment State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Pending Approval | Submit | Treasurer | valid amendment details | create proposal if needed |
| Pending Approval | Approved | Approval result | System/Approver | governance passed | ready to apply |
| Pending Approval | Rejected | Approval result | System/Approver | governance failed | notify requester |
| Approved | Applied | Apply amendment | Treasurer/System | original budget still active | update budget/version |
| Draft / Pending Approval | Cancelled | Cancel | Requester/Admin | not applied | log |

**C. Budget Utilization State Model**

Budget utilization entries are effectively immutable financial link records:

| **From** | **To** | **Trigger** | **Actor** | **Conditions** |
| --- | --- | --- | --- | --- |
| Created | Active | linked disbursement executed | System | execution valid |
| Active | Reversed | linked disbursement reversed | System | reversal exists |

**4.8.7 BUDGET CALCULATION ENGINE**

**A. Header Totals**

total_allocated = sum(line.allocated_amount for line in budget.lines)  
total_actual = sum(line.actual_amount for line in budget.lines)  
total_remaining = total_allocated - total_actual  
total_variance = total_actual - total_allocated

**B. Actual Spend Source**

Actuals shall be derived from:

- executed disbursement records linked to budget lines
- other explicitly budget-eligible actuals if later introduced

Actuals shall not be manually keyed directly into the line item except through controlled correction logic.

**C. Utilization Linkage Logic**

def apply_budget_utilization(execution, budget, line_ref):  
line = get_budget_line(budget, line_ref)  
create_utilization_entry(  
chama=budget.chama,  
budget=budget.name,  
budget_line_ref=line_ref,  
linked_disbursement_execution=execution.name,  
amount_utilized=execution.amount_executed  
)  
recompute_line_actuals(line)  
recompute_budget_totals(budget)

**4.8.8 OVERRUN ENGINE**

This is one of the most important controls.

**A. Overrun Modes**

| **Mode** | **Behavior** |
| --- | --- |
| Block | disallow disbursement that would exceed budget line |
| Warn | allow but flag overrun |
| Allow With Escalation | require higher approval before allowing overrun |

**B. Line-Level Check Formula**

projected_actual = current_actual_amount + proposed_disbursement_amount  
overrun = projected_actual - allocated_amount

**C. Enforcement Logic**

def check_budget_overrun(budget_line, proposed_amount, mode):  
projected = budget_line.actual_amount + proposed_amount  
if projected <= budget_line.allocated_amount:  
return {"status": "Within Budget"}  
<br/>if mode == "Block" or budget_line.requires_strict_control:  
return {"status": "Blocked", "overrun": projected - budget_line.allocated_amount}  
<br/>if mode == "Allow With Escalation":  
return {"status": "Escalate", "overrun": projected - budget_line.allocated_amount}  
<br/>return {"status": "Warn", "overrun": projected - budget_line.allocated_amount}

**D. Side Effects**

- Block → source disbursement cannot proceed
- Warn → source disbursement may proceed and overrun flag is set
- Escalate → source disbursement requires higher approval or proposal

**4.8.9 ACTION DEFINITIONS**

**A. Create Budget**

**Input**

{  
"chama": "CH-0001",  
"budget_name": "Q2 Welfare and Operations Budget",  
"budget_type": "MIXED",  
"period_start": "2026-04-01",  
"period_end": "2026-06-30",  
"overrun_mode": "Allow With Escalation",  
"line_items": \[  
{  
"category_name": "Welfare Support",  
"category_type": "Welfare",  
"allocated_amount": 50000  
},  
{  
"category_name": "Operations",  
"category_type": "Operations",  
"allocated_amount": 15000  
}  
\]  
}

**Process**

1.  validate dates
2.  validate line items > 0
3.  compute totals
4.  create budget in Draft

**Output**

{  
"status": "success",  
"data": {  
"budget_id": "BGT-0004",  
"budget_status": "Draft",  
"total_allocated": 65000  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| BG001 | Budget period invalid |
| BG002 | Budget must contain at least one valid line item |
| BG003 | Line allocation must be greater than zero |

**B. Submit Budget for Approval**

**Input**

{  
"budget_id": "BGT-0004"  
}

**Process**

- validate Draft status
- if approval_required:
    - create linked proposal
    - set Pending Approval
- else:
    - activate directly

**Output**

{  
"status": "success",  
"data": {  
"budget_id": "BGT-0004",  
"budget_status": "Pending Approval",  
"approval_proposal": "PRP-0012"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| BG101 | Budget not in submittable state |
| BG102 | Budget total must be greater than zero |
| BG103 | Approval proposal creation failed |

**C. Apply Approved Budget**

**Input**

{  
"budget_id": "BGT-0004"  
}

**Process**

- verify linked proposal approved or direct activation allowed
- set status Active
- stamp approved metadata

**Output**

{  
"status": "success",  
"data": {  
"budget_id": "BGT-0004",  
"budget_status": "Active"  
},  
"errors": \[\]  
}

**D. Create Budget Amendment**

**Input**

{  
"original_budget": "BGT-0004",  
"amendment_type": "Reallocation",  
"reason": "Increase welfare support allocation after emergency requests",  
"details": \[  
{  
"original_line_ref": "2",  
"amendment_action": "Decrease",  
"category_name": "Operations",  
"old_allocated_amount": 15000,  
"new_allocated_amount": 10000  
},  
{  
"original_line_ref": "1",  
"amendment_action": "Increase",  
"category_name": "Welfare Support",  
"old_allocated_amount": 50000,  
"new_allocated_amount": 55000  
}  
\]  
}

**Process**

- validate active budget
- create amendment in Draft
- compute deltas
- route for approval if needed

**Output**

{  
"status": "success",  
"data": {  
"amendment_id": "BGA-0002",  
"status": "Draft"  
},  
"errors": \[\]  
}

**E. Apply Amendment**

**Input**

{  
"amendment_id": "BGA-0002"  
}

**Process**

- verify Approved
- update line allocations
- increment budget version
- recalc totals
- mark amendment Applied

**Output**

{  
"status": "success",  
"data": {  
"budget_id": "BGT-0004",  
"active_version_no": 2,  
"amendment_status": "Applied"  
},  
"errors": \[\]  
}

**4.8.10 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Budget List (Desk/Web)**

**Columns**

- Budget ID
- Budget Name
- Type
- Period Start
- Period End
- Status
- Total Allocated
- Total Actual
- Total Remaining
- Version

**Filters**

- Chama
- Status
- Type
- Period
- Has Overrun

**Actions**

- New Budget
- Open
- Submit
- Activate
- Close
- Export

**B. Screen: Budget Detail (Desk)**

**Sections**

**1\. Budget Header**

| **Field** | **Type** |
| --- | --- |
| budget_name | Data |
| budget_type | Select |
| financial_period | Link |
| period_start | Date |
| period_end | Date |
| budget_status | Badge |
| overrun_mode | Select |
| active_version_no | Int |
| approval_proposal | Link |

**2\. Totals Panel**

| **Field** | **Type** |
| --- | --- |
| total_allocated | Currency |
| total_actual | Currency |
| total_remaining | Currency |
| total_variance | Currency |

**3\. Line Item Grid**

| **Field** | **Type** |
| --- | --- |
| category_name | Data |
| category_type | Select |
| allocated_amount | Currency |
| actual_amount | Currency |
| remaining_amount | Currency |
| utilization_percent | Percent |
| overrun_flag | Check |

**4\. Actions**

- Add Line
- Submit for Approval
- Activate
- Create Amendment
- Close Budget
- View Utilization Entries

**C. Screen: Budget Dashboard (Desk/Web)**

**Purpose**

Operational and management view.

**Cards**

- Total Active Budgets
- Total Allocated This Period
- Total Actual This Period
- Total Overrun Amount
- Budget Compliance Rate

**Charts**

- allocated vs actual by category
- budget utilization trend
- top overrun lines

**Drill-down**

click chart → budget detail or line item report

**D. Screen: Mobile Member Budget View**

**Purpose**

Transparency view for members.

**Display**

- active budgets
- summary totals
- high-level line item allocations
- status
- approval state

**Actions**

- View approved budget only
- no editing

**4.8.11 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View active budgets | Yes | Yes | Yes | Yes | Yes | Yes |
| View draft/pending budgets | Limited by policy | Yes | Yes | Yes | Yes | Yes |
| Create budget | No  | Yes | No  | Limited if configured | No  | Yes |
| Edit budget draft | No  | Yes | No  | Limited | No  | Yes |
| Submit budget | No  | Yes | No  | Yes if configured | No  | Yes |
| Activate approved budget | No  | Yes | Yes | No  | No  | Yes |
| Create amendment | No  | Yes | No  | Limited | No  | Yes |
| Apply amendment | No  | Yes | Yes | No  | No  | Yes |
| Close budget | No  | Yes | Yes | No  | No  | Yes |
| View all utilization entries | No  | Yes | Yes | No  | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Budget | total_allocated | Read active only | Read/Write draft | Read | Read |
| Budget | approval_proposal | Read approved only | Read | Read | Read |
| Budget Line | allocated_amount | Read active only | Write draft/amendment | Read | Read |
| Utilization | amount_utilized | No  | Read | Read | Read |

**C. Chama Scope Rule**

All budget, budget line, utilization, and amendment records must be filtered by:

doc.chama == current_user_selected_chama

**4.8.12 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| budget_submitted | submit for approval | approvers / members if governed | APP | budget_submitted | Medium |
| budget_approved | approval result | treasurer/chair/members | APP | budget_approved | Medium |
| budget_rejected | approval result | creator/chair | APP | budget_rejected | Medium |
| budget_overrun_warning | overrun mode warn | treasurer/chair | APP | budget_overrun_warning | High |
| budget_overrun_blocked | strict block triggered | requester/treasurer/chair | APP | budget_overrun_blocked | High |
| budget_amendment_submitted | amendment submit | approver(s) | APP | budget_amendment_submitted | Medium |
| budget_amendment_applied | amendment applied | treasurer/chair | APP | budget_amendment_applied | Medium |
| budget_closed | close | members / officials | APP | budget_closed | Low |

**Example Template: budget_overrun_warning**

Budget warning: proposed spend on {category_name} exceeds allocation by {overrun_amount}.

**Example Template: budget_approved**

The budget "{budget_name}" for {period_start} to {period_end} has been approved and is now active.

**4.8.13 API ENDPOINTS (FULL)**

**A. Create Budget**

POST /api/method/chama.budget.create

**B. Submit Budget**

POST /api/method/chama.budget.submit

**C. Activate Budget**

POST /api/method/chama.budget.activate

**D. Create Amendment**

POST /api/method/chama.budget.create_amendment

**E. Apply Amendment**

POST /api/method/chama.budget.apply_amendment

**F. Get Budget Detail**

GET /api/method/chama.budget.detail?budget=BGT-0004

**G. Get Active Budgets**

GET /api/method/chama.budget.list_active?chama=CH-0001

**H. Get Budget Dashboard**

GET /api/method/chama.budget.dashboard?chama=CH-0001&period=FP-2026-04

**Example Response**

{  
"status": "success",  
"data": {  
"budget_id": "BGT-0004",  
"budget_status": "Active",  
"total_allocated": 65000,  
"total_actual": 18000,  
"total_remaining": 47000,  
"line_items": \[  
{  
"category_name": "Welfare Support",  
"allocated_amount": 50000,  
"actual_amount": 12000,  
"remaining_amount": 38000,  
"overrun_flag": false  
}  
\]  
},  
"errors": \[\]  
}

**4.8.14 REPORTS**

**A. Budget Register**

**Columns**

- Budget ID
- Name
- Type
- Period
- Status
- Allocated
- Actual
- Remaining
- Version

**B. Budget vs Actual Report**

**Columns**

- Budget
- Line Item
- Allocated
- Actual
- Remaining
- Variance
- Utilization %

**C. Overrun Report**

**Columns**

- Budget
- Line Item
- Allocated
- Actual
- Overrun Amount
- Trigger Date
- Resolution Status

**D. Amendment History Report**

**Columns**

- Amendment ID
- Budget
- Type
- Reason
- Status
- Applied On
- Version Result

**E. Budget Compliance Metric**

**Formula**

budget_compliance_rate =  
(number_of_lines_without_overrun / total_active_budget_lines) \* 100

**4.8.15 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Budget | Required |
| Child Table | Chama Budget Line Item | Required |
| Custom DocType | Chama Budget Utilization Entry | Required |
| Custom DocType | Chama Budget Amendment | Required |
| Child Table | Chama Budget Amendment Detail | Required |
| Reports | register / vs actual / overrun / amendments | Required |
| Notifications | submit / approve / reject / overrun / amendment / close | Required |
| Integration | Voting proposal linkage | Required |
| Integration | Disbursement budget checks | Required |
| Dashboard | Budget Dashboard | Recommended |

**4.8.16 WORKFLOW CONFIGURATION**

**Workflow Name: Budget Approval**

| **State** | **Doc Status** | **Allow Edit By** | **Transition Action** |
| --- | --- | --- | --- |
| Draft | 0   | Treasurer/Secretary | Submit |
| Pending Approval | 0   | Approver/System | Approve / Reject |
| Active | final-ish operational | No structural edits except amendment path | Close |
| Rejected | final | No edit | End |
| Closed | final | Read only | End |
| Cancelled | final | Read only | End |

**Workflow Name: Budget Amendment Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Pending Approval | awaiting governance |
| Approved | ready to apply |
| Rejected | not approved |
| Applied | version updated |
| Cancelled | terminated |

**4.8.17 SERVER LOGIC / HOOKS**

**A. Recompute Budget Totals**

def recompute_budget_totals(budget):  
lines = get_budget_lines(budget)  
budget.total_allocated = sum(x.allocated_amount for x in lines)  
budget.total_actual = sum(x.actual_amount for x in lines)  
budget.total_remaining = budget.total_allocated - budget.total_actual  
budget.total_variance = budget.total_actual - budget.total_allocated  
budget.save()

**B. Apply Utilization After Disbursement**

def on_disbursement_executed(execution):  
if execution.disbursement_request and execution.disbursement_request.budget_item:  
budget, line_ref = resolve_budget_line_from_request(execution.disbursement_request)  
apply_budget_utilization(execution, budget, line_ref)

**C. Apply Amendment**

def apply_budget_amendment(amendment):  
budget = frappe.get_doc("Chama Budget", amendment.original_budget)  
ensure_budget_active(budget)  
ensure_amendment_approved(amendment)  
<br/>for row in amendment.details:  
apply_line_change(budget, row)  
<br/>budget.active_version_no += 1  
budget.save()  
<br/>amendment.status = "Applied"  
amendment.save()

**D. Overrun Check Hook**

def validate_disbursement_against_budget(request):  
if request.budget_item:  
result = check_budget_overrun_for_request(request)  
if result\["status"\] == "Blocked":  
frappe.throw("Budget overrun blocked this disbursement")  
elif result\["status"\] == "Escalate":  
mark_request_for_higher_approval(request, result)

**4.8.18 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Over-allocation at creation | sum/line validation | block save/submit | Yes |
| Amendment against closed budget | status check | block | Yes |
| Budget period overlap for same strict type | overlap check by Chama/type | warn or block per policy | Yes |
| Disbursement hits budget after line already overrun | live overrun check | apply overrun mode behavior | Yes |
| Budget approved but later source period cancelled | linked period state mismatch | warn and block close until resolved | Yes |
| Amendment approved but original budget changed in meantime | version mismatch | block apply, require reload/rebase | Yes |
| Budget with zero line items | creation validation | block submit | Yes |
| Negative line allocation through amendment | line validation | block | Yes |

**4.8.19 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | forecasted/actual inflows inform planning context |
| Disbursements | actual spend consumes budget lines |
| Voting & Resolutions | approval path for budgets and amendments |
| Meetings | budgets may be discussed in meetings |
| Reconciliation | actual outflows in statements must align with budget utilization |
| Analytics | dashboards consume budget vs actual metrics |
| Investments | investment budgets govern capital deployment |
| Notifications | budget events and overrun events emit notices |

**4.8.20 CRITICAL IMPLEMENTATION RULES**

- No active budget may exist without at least one valid line item
- Budget actuals must be derived from linked executed outflows, not manually keyed totals
- Overrun enforcement must occur at the point of spend validation, not only in reporting
- Amendments must not silently mutate history; they must create a visible version trail
- Every budget and budget-related record must include chama
- Active budgets must be read-only structurally except through amendment flow
- Budget approval status must not be inferred; it must be explicit and linked to governance evidence where required
- Budget totals displayed to users must exactly match underlying line sums

## MODULE 4.9 — MEMBER LIFECYCLE

**4.9.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Authentication user | ERPNext / Frappe User |
| Chama membership profile | Custom |
| Role assignment within Chama | Custom + ERPNext roles/role profiles |
| Status management | Custom |
| Onboarding and approval | Custom + Voting/Meetings where required |
| Suspension/reactivation | Custom |
| Exit and settlement | Custom + Contributions/Loans/Investments/Reconciliation integrations |
| Reporting and audit | ERPNext reports + custom logic |

**4.9.2 MODULE PURPOSE**

The Member Lifecycle module shall manage:

- member application and onboarding
- identity and contact capture
- linkage between ERPNext User and Chama-specific membership
- role assignment within each Chama
- member status changes
- suspension and reactivation
- dormancy handling
- member exit initiation
- exit settlement calculation
- closure of member obligations and entitlements
- auditability of all membership changes

This module must explicitly separate:

1.  **User**  
    the authentication account in ERPNext
2.  **Member Record**  
    the Chama-specific identity and participation record
3.  **Role Assignment**  
    the permissions and governance function of the member within a Chama
4.  **Status**  
    the lifecycle state controlling what the member can do
5.  **Exit Settlement**  
    the controlled financial closure process when a member leaves

That separation is mandatory.

**4.9.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall use a hybrid model:

**Reuse from ERPNext / Frappe**

- User DocType
- roles / role profiles
- permissions
- attachments
- workflow support
- reports
- audit/version patterns

**Custom Chama layer**

- Chama Member record
- Chama-specific role assignment record
- status engine
- onboarding approval path
- suspension/reactivation path
- exit request / settlement engine
- duplicate detection within Chama
- member financial summary rollup

**Rule**

A single ERPNext User may belong to multiple Chamas, but each Chama membership must be a distinct Chama Member record.

**4.9.4 STATUS MODEL**

The system shall support normalized member statuses:

| **Status Code** | **Label** | **Meaning** |
| --- | --- | --- |
| PENDING | Pending | Applied / not yet active |
| ACTIVE | Active | Full participation |
| SUSPENDED | Suspended | Restricted by governance/rules |
| DORMANT | Dormant | Inactive but not exited |
| EXIT_IN_PROGRESS | Exit In Progress | Settlement not completed |
| EXITED | Exited | Membership closed |
| REJECTED | Rejected | Application not approved |
| DECEASED | Deceased | Special handling state if required by policy |

**4.9.5 DATA MODEL (FULL)**

**A. DocType: Chama Member**

**Purpose**

Represents a member’s identity and participation within one Chama.

**DocType Type**

- Custom DocType
- Is Submittable: No
- Workflow optional
- Core tenant-scoped identity record

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Member ID | Data (Auto) | Yes | Example MB-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| user | User | Link(User) | No  | linked ERPNext user if available |
| full_name | Full Name | Data | Yes |     |
| first_name | First Name | Data | No  | optional split |
| last_name | Last Name | Data | No  | optional split |
| phone | Phone | Data | Yes | primary contact |
| email | Email | Data | No  |     |
| national_id | National ID | Data | Yes | unique within Chama; broader uniqueness policy configurable |
| date_of_birth | Date | No  |     |     |
| gender | Select | No  | optional |     |
| address_text | Small Text | No  |     |     |
| join_request_date | Date | No  |     |     |
| join_date | Date | No  | set on activation |     |
| exit_date | Date | No  | set on final exit |     |
| status | Select | Yes | lifecycle state |     |
| role_profile | Link(Role Profile) | No  | convenience/default |     |
| primary_role | Select | No  | Member/Treasurer/Chair/etc |     |
| tenure_months_snapshot | Int | No  | computed/derived where needed |     |
| onboarding_notes | Small Text | No  |     |     |
| suspension_reason | Small Text | No  |     |     |
| exit_reason | Small Text | No  |     |     |
| deceased_flag | Check | Yes | 0/1 |     |
| is_voting_eligible | Check | Yes | computed/configurable |     |
| is_loan_eligible | Check | Yes | computed/configurable |     |
| is_contribution_eligible | Check | Yes | computed/configurable |     |
| active_flag | Check | Yes | derived from status |     |
| created_by | Link(User) | Yes |     |     |
| created_on | Datetime | Yes |     |     |

**Status Enum**

Pending  
Active  
Suspended  
Dormant  
Exit In Progress  
Exited  
Rejected  
Deceased

**Constraints**

validate():  
ensure_required_identity_fields()  
enforce_unique_member_identity_within_chama()  
if status == "Active" and not join_date:  
frappe.throw("Join Date is required for active members")  
if exit_date and join_date and exit_date < join_date:  
frappe.throw("Exit Date cannot be before Join Date")

**B. DocType: Chama Member Role Assignment**

**Purpose**

Tracks role assignment history within a Chama.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Role Assignment ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | Yes |     |
| member | Link(Chama Member) | Yes |     |     |
| role_name | Select / Link(Role) | Yes |     |     |
| effective_from | Date | Yes |     |     |
| effective_to | Date | No  | nullable if active |     |
| active | Check | Yes | 1/0 |     |
| assigned_by | Link(User) | Yes |     |     |
| notes | Small Text | No  |     |     |

**Rule**

A member may hold multiple roles if policy allows, but only one active assignment per exclusive office role if configured.

**C. DocType: Chama Member Application**

**Purpose**

Captures an onboarding request separately from the final member record where approval is required.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Application ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| applicant_user | Link(User) | No  |     |
| full_name | Data | Yes |     |
| phone | Data | Yes |     |
| email | Data | No  |     |
| national_id | Data | Yes |     |
| address_text | Small Text | No  |     |
| application_date | Datetime | Yes |     |
| status | Select | Yes |     |
| proposed_role | Select | No  |     |
| approval_proposal | Link(Chama Proposal) | No  |     |
| reviewed_by | Link(User) | No  |     |
| reviewed_on | Datetime | No  |     |
| rejection_reason | Small Text | No  |     |

**Status Enum**

Draft  
Submitted  
Pending Approval  
Approved  
Rejected  
Cancelled

**D. DocType: Chama Member Status Change Log**

**Purpose**

Explicit audit trail of lifecycle state changes.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| member | Link(Chama Member) | Yes |
| from_status | Select | Yes |
| to_status | Select | Yes |
| reason | Small Text | Yes |
| changed_by | Link(User) | Yes |
| changed_on | Datetime | Yes |
| linked_resolution | Link(Chama Resolution) | No  |

**E. DocType: Chama Member Exit Request**

**Purpose**

Represents a member’s request or governance decision to leave.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Exit Request ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| member | Link(Chama Member) | Yes |     |
| exit_reason | Small Text | Yes |     |
| requested_date | Datetime | Yes |     |
| requested_by | Link(User) | Yes |     |
| status | Select | Yes |     |
| requires_approval | Check | Yes |     |
| approval_proposal | Link(Chama Proposal) | No  |     |
| settlement_id | Link(Chama Member Settlement) | No  |     |
| processed_by | Link(User) | No  |     |
| processed_on | Datetime | No  |     |

**Status Enum**

Draft  
Submitted  
Pending Approval  
Approved  
Rejected  
Settlement Pending  
Completed  
Cancelled

**F. DocType: Chama Member Settlement**

**Purpose**

Represents the financial settlement at exit.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Settlement ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | Yes |     |
| member | Link(Chama Member) | Yes |     |     |
| exit_request | Link(Chama Member Exit Request) | Yes |     |     |
| settlement_date | Date | Yes |     |     |
| shares_balance | Currency | Yes |     |     |
| contribution_balance | Currency | Yes |     |     |
| loan_outstanding | Currency | Yes |     |     |
| penalties_outstanding | Currency | Yes |     |     |
| guarantor_exposure_outstanding | Currency | Yes | contingent liability |     |
| investment_entitlement | Currency | Yes | computed/policy-based |     |
| benefit_offsets | Currency | Yes | if any |     |
| other_adjustments | Currency | Yes | signed amount if needed |     |
| final_payout_amount | Currency | Yes | computed |     |
| settlement_status | Select | Yes | Draft / Calculated / Approved / Paid / Closed / Cancelled |     |
| approved_by | Link(User) | No  |     |     |
| paid_by_execution | Link(Chama Disbursement Execution) | No  | payout link |     |
| notes | Small Text | No  |     |     |

**Settlement Status Enum**

Draft  
Calculated  
Approved  
Paid  
Closed  
Cancelled

**Formula**

Final Payout =  
shares_balance  
\+ contribution_balance  
\+ investment_entitlement  
\+ other_adjustments  
\- loan_outstanding  
\- penalties_outstanding  
\- benefit_offsets

guarantor_exposure_outstanding is shown separately because policy may:

- block exit,
- require transfer,
- or hold part of settlement.

**4.9.6 STATE MACHINES (FORMAL)**

**A. Member Application State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit application | Applicant/Admin | required fields valid | notify reviewers |
| Submitted | Pending Approval | Route for governance | System/Secretary | approval required | create proposal if needed |
| Submitted / Pending Approval | Approved | Approve | Chair/System | criteria satisfied | create member record |
| Submitted / Pending Approval | Rejected | Reject | Chair/System | —   | notify applicant |
| Draft / Submitted | Cancelled | Cancel | Applicant/Admin | not finalized | log |

**B. Member Status State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Pending | Active | Approve application | Chair/System | onboarding complete | set join_date, create obligations eligibility |
| Active | Suspended | Suspend | Chair/Admin/System | breach or policy event | restrict permissions/actions |
| Suspended | Active | Reinstate | Chair/Admin | issue resolved | restore permissions |
| Active | Dormant | Mark dormant | Admin/System | inactivity threshold or policy | restrict optional actions |
| Dormant | Active | Reactivate | Admin/Chair | return to active participation | restore |
| Active / Dormant / Suspended | Exit In Progress | Exit initiated | Member/Admin/System | exit request accepted | block new obligations/actions |
| Exit In Progress | Exited | Settlement closed | System/Admin | payout/closure complete | finalize member |
| Pending | Rejected | Reject application | Chair/System | —   | no active membership |
| Any relevant | Deceased | Mark deceased | Admin/Chair | verified event | special handling |

**C. Exit Request State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit | Member/Admin | reason present | notify reviewer |
| Submitted | Pending Approval | Route | System | approval required | create proposal if needed |
| Submitted / Pending Approval | Approved | Approve | Chair/System | allowed | create settlement draft |
| Submitted / Pending Approval | Rejected | Reject | Chair/System | —   | notify member |
| Approved | Settlement Pending | Start settlement | Treasurer/System | member status moved to Exit In Progress | calculate balances |
| Settlement Pending | Completed | settlement closed | System/Admin | payout/closure done | set member Exited |
| Draft / Submitted | Cancelled | Cancel | Member/Admin | not finalized | log |

**D. Settlement State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Calculated | Calculate | Treasurer/System | source balances loaded | freeze computed figures |
| Calculated | Approved | Approve | Chair/Treasurer per policy | valid review | ready for payout |
| Approved | Paid | Payout executed | Treasurer/System | disbursement succeeded or zero payout closure | link execution |
| Paid | Closed | Close settlement | System/Admin | all post-checks pass | finalize member status |
| Draft / Calculated / Approved | Cancelled | Cancel | Admin | policy exception | log |

**4.9.7 ONBOARDING ENGINE**

**A. Onboarding Modes**

| **Mode** | **Description** |
| --- | --- |
| Admin Direct | official creates member directly |
| Application Approval | applicant submits and is approved |
| Bulk Migration | initial import of existing Chama members |

**B. Duplicate Detection**

Potential duplicates shall be checked within Chama using:

- national_id
- phone
- email (if present)

Configurable cross-Chama warning may be shown, but not automatically blocked unless policy requires.

**C. Activation Side Effects**

When a member becomes Active:

- join_date must be set
- role assignment created if applicable
- contribution generation eligibility enabled
- voting eligibility evaluated
- notification sent
- status change log recorded

**4.9.8 ROLE ASSIGNMENT ENGINE**

**A. Standard Roles**

| **Role** | **Meaning** |
| --- | --- |
| Member | standard participant |
| Treasurer | finance operations |
| Chair | governance approvals |
| Secretary | meetings and records |
| Auditor | oversight |
| Committee | special committee role |

**B. Assignment Rules**

- role assignments are Chama-scoped
- effective date required
- exclusive leadership roles may have one active assignee at a time if configured
- assigning/removing a role updates permission context

**C. Pseudocode**

def assign_member_role(member, role_name, effective_from):  
close_conflicting_role_assignments(member.chama, role_name, effective_from)  
create_role_assignment(member, role_name, effective_from)  
sync_user_permissions(member.user, member.chama)

**4.9.9 STATUS EFFECTS ENGINE**

This is critical. Status must drive behavior across the system.

| **Member Status** | **Contributions** | **Loans** | **Voting** | **Meetings** | **Disbursements** | **Exit** |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | No new obligations by default | Not eligible | Not eligible | View limited if policy | Not eligible unless applicant refund etc | Not applicable |
| Active | Eligible | Eligible subject to rules | Eligible | Eligible | Eligible as beneficiary | Can initiate |
| Suspended | Existing obligations remain; new optional generation configurable | Not eligible | Not eligible | View only / limited | Restricted | Can be forced/processed |
| Dormant | Configurable | Usually not eligible | Usually not eligible | View only | Restricted | Can initiate/reactivate |
| Exit In Progress | No new obligations | Not eligible | Not eligible | Read only | Settlement only | In process |
| Exited | Historical read only | Not eligible | Not eligible | Historical read only | Settlement history only | Final |
| Rejected | No access beyond application outcome | Not eligible | Not eligible | None | None | Not applicable |
| Deceased | Special handling | No new actions | No voting | Historical only | estate/benefit policy only | special closure |

**4.9.10 EXIT & SETTLEMENT ENGINE**

This is one of the highest-risk areas and must be explicit.

**A. Exit Preconditions**

Before final exit, system must check:

- outstanding contribution arrears
- active loan balances
- penalties outstanding
- guarantor obligations still active
- open committee/governance obligations if configured
- investment lock or unresolved entitlement
- pending disbursements or credits

**B. Policy Handling Modes for Guarantor Exposure**

| **Mode** | **Behavior** |
| --- | --- |
| Block Exit | cannot proceed until exposure cleared |
| Hold Settlement | exit may proceed but part/all payout held |
| Transfer Required | exposure must be reassigned |
| Informational Only | warn but allow exit |

**C. Settlement Calculation Steps**

1.  fetch member balances
2.  fetch outstanding obligations
3.  compute investment entitlement
4.  compute offsets
5.  compute provisional payout
6.  apply policy checks
7.  approve settlement
8.  execute payout or zero-close
9.  set member Exited

**D. Pseudocode**

def calculate_member_settlement(member):  
shares = get_member_shares_balance(member)  
contributions = get_member_contribution_balance(member)  
loans = get_member_loan_outstanding(member)  
penalties = get_member_penalties(member)  
investments = get_member_investment_entitlement(member)  
offsets = get_member_other_offsets(member)  
<br/>payout = shares + contributions + investments + offsets - loans - penalties  
return {  
"shares_balance": shares,  
"contribution_balance": contributions,  
"loan_outstanding": loans,  
"penalties_outstanding": penalties,  
"investment_entitlement": investments,  
"other_adjustments": offsets,  
"final_payout_amount": payout  
}

**E. Exit Side Effects**

- member status -> Exit In Progress then Exited
- new loan/contribution/vote activity blocked
- final statement generated
- settlement record stored
- payout linked if payable
- historical records retained

**4.9.11 ACTION DEFINITIONS**

**A. Submit Member Application**

**Input**

{  
"chama": "CH-0001",  
"full_name": "Jane Doe",  
"phone": "+254700000000",  
"email": "jane@example.com",  
"national_id": "12345678",  
"address_text": "Nairobi",  
"proposed_role": "Member"  
}

**Process**

1.  validate required fields
2.  run duplicate checks
3.  create application in Submitted or Pending Approval
4.  notify reviewers

**Output**

{  
"status": "success",  
"data": {  
"application_id": "MAP-0004",  
"status": "Submitted"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MB001 | Duplicate member identity detected in this Chama |
| MB002 | Required identity fields missing |
| MB003 | Chama is not accepting new members |

**B. Approve Member Application**

**Input**

{  
"application_id": "MAP-0004"  
}

**Process**

- validate approver authority
- create Chama Member
- set status Active
- set join_date
- create role assignment if needed
- notify applicant

**Output**

{  
"status": "success",  
"data": {  
"member_id": "MB-0021",  
"status": "Active"  
},  
"errors": \[\]  
}

**C. Change Member Status**

**Input**

{  
"member_id": "MB-0021",  
"to_status": "Suspended",  
"reason": "Persistent rule breach"  
}

**Process**

- validate allowed transition
- create status change log
- update permissions/effects
- notify relevant users

**Output**

{  
"status": "success",  
"data": {  
"member_id": "MB-0021",  
"status": "Suspended"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MB101 | Invalid status transition |
| MB102 | Reason is required |
| MB103 | User not authorized |

**D. Assign Role**

**Input**

{  
"member_id": "MB-0021",  
"role_name": "Treasurer",  
"effective_from": "2026-05-01"  
}

**Process**

- validate exclusivity rules
- create active role assignment
- sync permissions

**Output**

{  
"status": "success",  
"data": {  
"role_assignment_id": "MRA-0003"  
},  
"errors": \[\]  
}

**E. Initiate Exit**

**Input**

{  
"member_id": "MB-0021",  
"exit_reason": "Relocation"  
}

**Process**

- create exit request
- route for approval if required
- set member status to Exit In Progress when approved

**Output**

{  
"status": "success",  
"data": {  
"exit_request_id": "MEX-0002",  
"status": "Submitted"  
},  
"errors": \[\]  
}

**F. Calculate Settlement**

**Input**

{  
"exit_request_id": "MEX-0002"  
}

**Process**

- load balances
- compute payout
- create settlement Draft/Calculated

**Output**

{  
"status": "success",  
"data": {  
"settlement_id": "MST-0002",  
"final_payout_amount": 12500  
},  
"errors": \[\]  
}

**G. Finalize Exit**

**Input**

{  
"settlement_id": "MST-0002"  
}

**Process**

- verify settlement approved
- verify payout completed or no payout due
- set member status Exited
- set exit_date
- close exit request

**Output**

{  
"status": "success",  
"data": {  
"member_id": "MB-0021",  
"status": "Exited",  
"exit_date": "2026-05-15"  
},  
"errors": \[\]  
}

**4.9.12 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Member List (Desk)**

**Columns**

- Member ID
- Full Name
- Phone
- Primary Role
- Status
- Join Date
- Chama

**Filters**

- Chama
- Status
- Role
- Join Date
- Voting Eligible
- Loan Eligible

**Actions**

- New Member
- Approve Application
- Change Status
- Assign Role
- Initiate Exit
- Export

**B. Screen: Member Profile (Desk)**

**Sections**

**1\. Identity**

| **Field** | **Type** |
| --- | --- |
| full_name | Data |
| phone | Data |
| email | Data |
| national_id | Data |
| address_text | Small Text |
| status | Badge |

**2\. Membership**

| **Field** | **Type** |
| --- | --- |
| join_date | Date |
| exit_date | Date |
| primary_role | Select |
| active_flag | Check |
| is_voting_eligible | Check |
| is_loan_eligible | Check |

**3\. Financial Summary**

| **Field** | **Type** |
| --- | --- |
| contribution_balance | Currency |
| outstanding_loans | Currency |
| penalties_outstanding | Currency |
| guarantor_exposure | Currency |
| investment_entitlement | Currency |

**4\. Actions**

- Change Status
- Assign Role
- View Member Statement
- Initiate Exit
- View Settlement

**C. Screen: Member Application (Mobile/Web)**

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| full_name | Data | Yes |
| phone | Data | Yes |
| email | Data | No  |
| national_id | Data | Yes |
| address_text | Small Text | No  |
| proposed_role | Select | No  |

**Actions**

- Save Draft
- Submit Application

**D. Screen: Exit Settlement View (Desk)**

**Sections**

- member summary
- liabilities
- entitlements
- final payout
- policy flags (e.g. guarantor exposure)
- linked payout execution

**Actions**

- Calculate
- Approve
- Pay / Link Payout
- Close Settlement

**E. Screen: Member Self Profile (Mobile)**

**Display**

- basic profile
- current status
- Chama role(s)
- join date
- own financial summary
- own exit request status if any

**Actions**

- Request profile update (future)
- Initiate Exit if allowed
- View own member statement

**4.9.13 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View own member profile | Yes | Yes | Yes | Yes | Yes | Yes |
| View all members in Chama | No  | Yes | Yes | Yes | Yes | Yes |
| Create member application | Yes | Yes | No  | No  | No  | Yes |
| Approve/reject application | No  | No  | Yes | Limited if configured | No  | Yes |
| Change member status | No  | Limited | Yes | No  | No  | Yes |
| Assign role | No  | No  | Yes | No  | No  | Yes |
| Initiate exit for self | Yes if policy allows | No  | No  | No  | No  | Yes |
| Initiate forced/admin exit | No  | No  | Yes | No  | No  | Yes |
| Calculate settlement | No  | Yes | Yes | No  | No  | Yes |
| Approve settlement | No  | Limited if configured | Yes | No  | No  | Yes |
| Finalize exit | No  | Yes | Yes | No  | No  | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Member | national_id | Read own only | Read | Read | Read |
| Member | suspension_reason | No  | Read | Write/Read | Read |
| Settlement | final_payout_amount | Read own after approval if policy | Read | Read/Approve | Read |
| Role Assignment | role_name | Read own | Read | Write | Read |

**C. Chama Scope Rule**

All member, application, role assignment, status log, exit request, and settlement records must be filtered by:

doc.chama == current_user_selected_chama

**4.9.14 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| member_application_received | application submit | chair/secretary/reviewer | APP | member_application_received | Medium |
| member_approved | approval | applicant/member | APP, SMS | member_approved | Medium |
| member_rejected | rejection | applicant | APP | member_rejected | Medium |
| member_suspended | status -> Suspended | member + chair/treasurer | APP, SMS | member_suspended | High |
| member_reactivated | status -> Active | member | APP | member_reactivated | Medium |
| exit_initiated | exit request submitted | treasurer/chair | APP | exit_initiated | Medium |
| settlement_ready | settlement calculated | approver/treasurer | APP | settlement_ready | Medium |
| exit_completed | final exit | member/officials | APP | exit_completed | Medium |

**Example Template: member_suspended**

Your membership status in {chama_name} has been changed to Suspended. Reason: {reason}.

**Example Template: exit_completed**

Your exit from {chama_name} has been completed. Final settlement amount: {final_payout_amount}.

**4.9.15 API ENDPOINTS (FULL)**

**A. Submit Member Application**

POST /api/method/chama.member.apply

**B. Approve Member Application**

POST /api/method/chama.member.approve_application

**C. Reject Member Application**

POST /api/method/chama.member.reject_application

**D. Get Member Profile**

GET /api/method/chama.member.profile?member=MB-0021

**E. Change Status**

POST /api/method/chama.member.change_status

**F. Assign Role**

POST /api/method/chama.member.assign_role

**G. Initiate Exit**

POST /api/method/chama.member.initiate_exit

**H. Calculate Settlement**

POST /api/method/chama.member.calculate_settlement

**I. Finalize Exit**

POST /api/method/chama.member.finalize_exit

**Example Response**

{  
"status": "success",  
"data": {  
"member_id": "MB-0021",  
"status": "Active",  
"primary_role": "Member"  
},  
"errors": \[\]  
}

**4.9.16 REPORTS**

**A. Member Register**

**Columns**

- Member ID
- Full Name
- Phone
- Status
- Join Date
- Primary Role

**B. Membership Status Report**

**Columns**

- Member
- Current Status
- Last Status Change
- Reason
- Voting Eligible
- Loan Eligible

**C. Role Assignment History**

**Columns**

- Member
- Role
- Effective From
- Effective To
- Active

**D. Exit & Settlement Register**

**Columns**

- Exit Request ID
- Member
- Exit Reason
- Settlement ID
- Final Payout
- Settlement Status
- Exit Date

**E. Inactive / Dormant Members Report**

**Purpose**

Operational follow-up and governance review.

**4.9.17 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Member | Required |
| Custom DocType | Chama Member Role Assignment | Required |
| Custom DocType | Chama Member Application | Recommended if approval path exists |
| Custom DocType | Chama Member Status Change Log | Required |
| Custom DocType | Chama Member Exit Request | Required |
| Custom DocType | Chama Member Settlement | Required |
| Reports | member register / status / roles / exits | Required |
| Notifications | application / status / exit / settlement | Required |
| Integration | Proposal linkage for approvals | Required where governed |

**4.9.18 WORKFLOW CONFIGURATION**

**Workflow Name: Member Application Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Submitted | received |
| Pending Approval | under governance |
| Approved | accepted |
| Rejected | declined |
| Cancelled | withdrawn/closed |

**Workflow Name: Member Exit**

| **State** | **Meaning** |
| --- | --- |
| Draft | prepared |
| Submitted | received |
| Pending Approval | under review |
| Approved | approved to proceed |
| Settlement Pending | waiting financial closure |
| Completed | fully exited |
| Cancelled | stopped |

**Workflow Name: Settlement Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Calculated | computed |
| Approved | approved |
| Paid | payout executed |
| Closed | fully complete |
| Cancelled | terminated |

**4.9.19 SERVER LOGIC / HOOKS**

**A. Approve Member**

def approve_member_application(application):  
ensure_application_approvable(application)  
member = create_member_from_application(application)  
member.status = "Active"  
member.join_date = today()  
member.save()  
log_status_change(member, "Pending", "Active", "Application approved")  
notify_member_approved(member)

**B. Change Status**

def change_member_status(member, to_status, reason, changed_by):  
ensure_valid_member_transition(member.status, to_status)  
old = member.status  
member.status = to_status  
member.active_flag = 1 if to_status == "Active" else 0  
member.save()  
create_status_change_log(member, old, to_status, reason, changed_by)  
sync_member_entitlements(member)

**C. Calculate Settlement**

def calculate_member_settlement_for_exit(exit_request):  
member = frappe.get_doc("Chama Member", exit_request.member)  
values = calculate_member_settlement(member)  
<br/>settlement = frappe.get_doc({  
"doctype": "Chama Member Settlement",  
"chama": member.chama,  
"member": member.name,  
"exit_request": exit_request.name,  
"settlement_date": today(),  
\*\*values,  
"settlement_status": "Calculated"  
}).insert()  
<br/>return settlement

**D. Finalize Exit**

def finalize_member_exit(settlement):  
ensure_settlement_closable(settlement)  
member = frappe.get_doc("Chama Member", settlement.member)  
member.status = "Exited"  
member.exit_date = settlement.settlement_date  
member.active_flag = 0  
member.save()  
log_status_change(member, "Exit In Progress", "Exited", "Settlement completed")

**4.9.20 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Duplicate member application | matching ID/phone | block or flag for review | Yes |
| User belongs to multiple Chamas | same User linked to multiple members | allow, keep records separate | Yes |
| Member exits with active loan | loan outstanding > 0 | block exit or offset via settlement per policy | Yes |
| Member exits with guarantor exposure | active guarantees exist | block / hold / transfer based on policy | Yes |
| Role conflict (e.g. two treasurers where exclusive) | active assignment check | block or require closure of prior assignment | Yes |
| Suspended member tries to vote/apply for loan | status check | reject action | Yes |
| Deceased member with investment entitlement | deceased flag + open assets | special settlement path | Yes |
| Re-joining after exit | previous member exists | create new application or reactivation policy path | Yes |

**4.9.21 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | active status controls obligation generation |
| Loans | tenure/status/role affect eligibility; exit needs loan balances |
| Voting | status controls voting eligibility |
| Meetings | active members form quorum basis |
| Disbursements | member may be beneficiary or settlement payout recipient |
| Investments | exit settlement includes investment entitlement |
| Notifications | lifecycle events generate notices |
| Analytics | member counts, dormancy, churn, tenure metrics consume lifecycle data |

**4.9.22 CRITICAL IMPLEMENTATION RULES**

- Every member record must include chama
- User identity and member identity must be separated conceptually and structurally
- Member status must drive permissions and eligibility across modules
- Exit must never be treated as a simple status toggle; it requires settlement workflow
- Historical membership records must remain preserved after exit
- Role changes must be time-bounded and auditable
- Member duplicates within a Chama must be prevented or explicitly reviewed
- Settlement totals must be reproducible from underlying balances and formulas

## MODULE 4.10 — INVESTMENT MANAGEMENT

**4.10.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Investment master record | Custom |
| Funding linkage | Custom + Contributions / Disbursements integrations |
| Ownership allocation | Custom |
| Valuation history | Custom |
| Return distribution | Custom + Disbursements module |
| Governance approval | Voting & Resolutions / Meetings |
| Member exit implications | Member Lifecycle + Settlement |
| Reporting and dashboards | ERPNext reports + custom logic |

**4.10.2 MODULE PURPOSE**

The Investment Management module shall manage:

- creation of investment proposals
- approval of investments before activation
- recording of acquired assets
- classification of investment types
- tracking of how investments were funded
- ownership allocation among members
- changes in valuation over time
- recording of returns generated by investments
- return distribution to members
- partial sale or closure of investments
- member exit treatment where investments remain open or illiquid

This module must explicitly separate:

1.  **Investment Proposal**  
    the planned asset or venture before acquisition
2.  **Investment Record**  
    the active investment after approval/acquisition
3.  **Funding Record**  
    how the investment was financed
4.  **Ownership Allocation**  
    the entitlement of members in the investment
5.  **Valuation Record**  
    the periodic estimate or measured value of the investment
6.  **Return Event**  
    income or realized proceeds from the investment

That separation is mandatory.

**4.10.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall be primarily custom because ERPNext does not natively model Chama-style pooled ownership and member-linked investment entitlements in the exact way needed.

**Reuse from ERPNext / Frappe**

- DocTypes and child tables
- attachments
- workflows where useful
- reports and dashboards
- roles and permissions
- audit/version patterns

**Custom Chama layer**

- investment proposal and approval flow
- active investment records
- ownership allocation engine
- valuation history
- return generation and distribution logic
- exit entitlement and liquidity policy handling
- cross-linkage to budgets, meetings, and resolutions

**Rule**

Do not reduce investment management to a single ledger line or generic asset row.  
A Chama investment is both:

- a financial asset
- a social ownership construct

Both sides must be modeled.

**4.10.4 INVESTMENT TYPES**

The system shall support normalized investment types:

| **Type Code** | **Label** | **Description** |
| --- | --- | --- |
| LAND | Land / Plot | land parcels and property purchase |
| BUSINESS | Business Venture | shops, farms, ventures, partnerships |
| FIN_ASSET | Financial Asset | stocks, bonds, unit trusts, fixed-income placements |
| EQUIPMENT | Equipment / Machinery | productive assets |
| PROPERTY | Rental / Property Asset | property producing rent or occupancy value |
| LIVESTOCK | Livestock / Agricultural Asset | livestock, farming assets |
| OTHER | Other Investment | configured catch-all |

**4.10.5 OWNERSHIP MODELS**

The system shall support at least the following ownership models:

| **Model Code** | **Label** | **Description** |
| --- | --- | --- |
| EQUAL | Equal Ownership | all eligible members share equally |
| CONTRIBUTION | Contribution-Based | ownership proportional to funding contribution |
| HYBRID | Hybrid | equal base plus weighted component |
| UNITIZED | Unit-Based | ownership tracked in units purchased |
| MANUAL | Manual Allocation | explicit admin-defined allocation with audit |

**4.10.6 DATA MODEL (FULL)**

**A. DocType: Chama Investment Proposal**

**Purpose**

Represents an investment idea/proposal before acquisition or activation.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Proposal ID | Data (Auto) | Yes | Example INP-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| title | Title | Data | Yes |     |
| investment_type | Select | Yes | from investment types |     |
| proposal_description | Long Text | Yes |     |     |
| estimated_cost | Currency | Yes |     |     |
| proposed_acquisition_date | Date | No  |     |     |
| ownership_model | Select | Yes | from ownership models |     |
| proposed_funding_source | Select | No  | Contributions / Levy / Reserve / Mixed / External |     |
| linked_budget | Link(Chama Budget) | No  | if budget-backed |     |
| approval_proposal | Link(Chama Proposal) | No  | governance vote linkage |     |
| status | Select | Yes | Draft / Pending Approval / Approved / Rejected / Cancelled / Converted |     |
| created_by | Link(User) | Yes |     |     |
| notes | Small Text | No  |     |     |

**Status Enum**

Draft  
Pending Approval  
Approved  
Rejected  
Cancelled  
Converted

**B. DocType: Chama Investment**

**Purpose**

Represents an approved/active investment asset or venture.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Investment ID | Data (Auto) | Yes | Example INV-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| title | Title | Data | Yes |     |
| investment_type | Select | Yes |     |     |
| ownership_model | Select | Yes |     |     |
| acquisition_date | Date | Yes |     |     |
| acquisition_cost | Currency | Yes |     |     |
| currency | Link(Currency) | Yes |     |     |
| status | Select | Yes | Draft / Active / Partially Realized / Closed / Cancelled |     |
| proposal_source | Link(Chama Investment Proposal) | No  | original proposal |     |
| linked_budget | Link(Chama Budget) | No  | if acquired under budget |     |
| linked_disbursement_execution | Link(Chama Disbursement Execution) | No  | acquisition payout |     |
| asset_description | Long Text | No  |     |     |
| asset_identifier | Data | No  | title number / account number / asset code |     |
| ownership_locked | Check | Yes | 0/1 | whether allocation locked after acquisition |
| current_valuation | Currency | Yes | latest computed/approved valuation |     |
| total_realized_returns | Currency | Yes | cumulative |     |
| total_unrealized_gain_loss | Currency | Yes | current_valuation - acquisition_cost |     |
| exit_liquidity_policy | Select | Yes | Hold / Payout If Realized / Transfer Units / Manual |     |
| created_by | Link(User) | Yes |     |     |
| created_on | Datetime | Yes |     |     |

**Status Enum**

Draft  
Active  
Partially Realized  
Closed  
Cancelled

**Computed Rule**

total_unrealized_gain_loss = current_valuation - acquisition_cost

**C. Child Table: Chama Investment Funding**

**Parent**

Chama Investment

**Purpose**

Breaks down how the investment was financed.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| funding_type | Select | Yes | Contribution / Special Levy / Reserve / External / Mixed |     |
| source_reference | Data / Dynamic Link | No  | contribution batch / budget / disbursement |     |
| amount | Currency | Yes |     |     |
| funding_date | Date | No  |     |     |
| notes | Small Text | No  |     |     |

**D. Child Table: Chama Investment Ownership**

**Parent**

Chama Investment

**Purpose**

Represents each member’s ownership allocation.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| member | Link(Chama Member) | Yes | owner member |     |
| ownership_percent | Percent | No  | used in percentage models |     |
| ownership_units | Float | No  | used in unitized models |     |
| contributed_amount | Currency | No  | contribution basis |     |
| current_entitlement_value | Currency | Yes | computed |     |
| active | Check | Yes | 1/0 |     |
| notes | Small Text | No  |     |     |

**Constraints**

- total ownership must satisfy model-specific rules
- for percentage models, total active ownership should = 100%
- for unitized models, percentages may be derived

**E. DocType: Chama Investment Valuation**

**Purpose**

Stores one valuation event.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Valuation ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| investment | Link(Chama Investment) | Yes |     |
| valuation_date | Date | Yes |     |
| valuation_amount | Currency | Yes |     |
| valuation_method | Select | Yes |     |
| valuation_basis_note | Small Text | Yes |     |
| prepared_by | Link(User) | Yes |     |
| approved_by | Link(User) | No  |     |
| status | Select | Yes |     |

**Valuation Methods**

- Market Estimate
- External Appraisal
- Book Value
- Income-Based
- Manual Committee Assessment

**Status Enum**

Draft  
Submitted  
Approved  
Rejected  
Applied  
Cancelled

**Rule**

Only one valuation may be the active current valuation at a time after approval/application.

**F. DocType: Chama Investment Return Event**

**Purpose**

Represents income or realized return generated by an investment.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Return Event ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| investment | Link(Chama Investment) | Yes |     |
| return_type | Select | Yes |     |
| event_date | Date | Yes |     |
| gross_amount | Currency | Yes |     |
| expenses_deducted | Currency | Yes |     |
| net_amount | Currency | Yes |     |
| realization_type | Select | Yes |     |
| distribution_status | Select | Yes |     |
| linked_disbursement_batch_ref | Data | No  |     |
| notes | Small Text | No  |     |

**Return Types**

- Rent
- Profit Share
- Dividend
- Sale Proceeds
- Interest
- Other

**Realization Types**

- Cash Realized
- Book Adjustment
- Partial Realization
- Full Exit

**Distribution Status Enum**

Undistributed  
Partially Distributed  
Distributed  
Held  
Cancelled

**Computed Rule**

net_amount = gross_amount - expenses_deducted

**G. DocType: Chama Investment Distribution**

**Purpose**

Stores per-member distribution generated from a return event.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Distribution ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| return_event | Link(Chama Investment Return Event) | Yes |     |
| investment | Link(Chama Investment) | Yes |     |
| member | Link(Chama Member) | Yes |     |
| ownership_basis_snapshot | Float / JSON | Yes |     |
| distribution_amount | Currency | Yes |     |
| distribution_status | Select | Yes |     |
| linked_disbursement_execution | Link(Chama Disbursement Execution) | No  |     |
| notes | Small Text | No  |     |

**Distribution Status Enum**

Calculated  
Approved  
Paid  
Held  
Cancelled

**4.10.7 STATE MACHINES (FORMAL)**

**A. Investment Proposal State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Pending Approval | Submit | Treasurer/Secretary | valid fields | create governance proposal if needed |
| Pending Approval | Approved | Approval result | System/Chair | resolution approved | allow conversion |
| Pending Approval | Rejected | Approval result | System/Chair | resolution rejected | notify proposer |
| Draft / Pending Approval | Cancelled | Cancel | Creator/Admin | not converted | log |
| Approved | Converted | Convert to investment | Treasurer/Admin | acquisition details complete | create investment record |

**B. Investment State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Active | Activate | Treasurer/Admin | acquisition completed, ownership set | initialize valuation |
| Active | Partially Realized | partial sale/realization | Treasurer/Admin | realization event recorded | update returns/liquidity |
| Active / Partially Realized | Closed | full disposal / closure | Treasurer/Admin | no remaining ownership or asset closed | finalize |
| Draft | Cancelled | Cancel | Admin | not active | log |

**C. Valuation State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit | Treasurer/Reviewer | note present | notify approver |
| Submitted | Approved | Approve | Chair/Authorized reviewer | valid valuation | ready to apply |
| Submitted | Rejected | Reject | Reviewer | —   | notify preparer |
| Approved | Applied | Apply | System/Treasurer | investment active | update current valuation |
| Draft / Submitted | Cancelled | Cancel | Creator/Admin | not applied | log |

**D. Return Event State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Created | Undistributed | Save event | Treasurer | net amount valid | ready for calculation |
| Undistributed | Partially Distributed | some distributions paid | System | partial payout state | update |
| Undistributed / Partially Distributed | Distributed | all distributions paid | System | all linked payouts done | update cumulative totals |
| Any prefinal | Held | hold decision | Treasurer/Chair | policy reason | no payout |
| Any prefinal | Cancelled | cancel | Admin | invalid event | reverse implications if needed |

**4.10.8 OWNERSHIP ALLOCATION ENGINE**

This is central and must be precise.

**A. Equal Ownership**

ownership_percent = 100 / number_of_active_owners

**B. Contribution-Based Ownership**

ownership_percent =  
member_contributed_amount / total_contributed_amount \* 100

**C. Unitized Ownership**

ownership_percent =  
member_units / total_units \* 100

**D. Hybrid Ownership**

Hybrid formula must be explicitly configured. Example:

ownership_percent =  
(0.5 \* equal_share_component) + (0.5 \* contribution_weight_component)

**E. Pseudocode**

def recalculate_investment_ownership(investment):  
owners = get_active_owners(investment)  
<br/>if investment.ownership_model == "EQUAL":  
pct = 100 / len(owners) if owners else 0  
for o in owners:  
o.ownership_percent = pct  
<br/>elif investment.ownership_model == "CONTRIBUTION":  
total = sum(o.contributed_amount for o in owners)  
for o in owners:  
o.ownership_percent = (o.contributed_amount / total \* 100) if total else 0  
<br/>elif investment.ownership_model == "UNITIZED":  
total_units = sum(o.ownership_units for o in owners)  
for o in owners:  
o.ownership_percent = (o.ownership_units / total_units \* 100) if total_units else 0  
<br/>save_all(owners)

**F. Validation Rules**

- for percentage-based models, total active ownership must equal 100% within rounding tolerance
- for equal model, manual override not allowed unless policy enables
- ownership changes after lock require amendment trail

**4.10.9 VALUATION ENGINE**

**A. Current Valuation Update Rule**

Only an Approved + Applied valuation updates current_valuation.

**B. Unrealized Gain/Loss Formula**

unrealized_gain_loss = current_valuation - acquisition_cost

**C. Member Entitlement Value**

member_entitlement_value =  
current_valuation \* ownership_percent / 100

**D. Pseudocode**

def apply_investment_valuation(valuation):  
ensure_valuation_approved(valuation)  
inv = frappe.get_doc("Chama Investment", valuation.investment)  
inv.current_valuation = valuation.valuation_amount  
inv.total_unrealized_gain_loss = inv.current_valuation - inv.acquisition_cost  
inv.save()  
refresh_owner_entitlements(inv)

**4.10.10 RETURN DISTRIBUTION ENGINE**

**A. Distribution Basis**

By default, return distributions are allocated using ownership snapshot at event date.

**B. Formula**

distribution_amount =  
return_event.net_amount \* member_ownership_percent / 100

**C. Held Returns**

Where policy requires retention or reserve:

- return event may remain Held
- no distribution rows are paid until approved

**D. Pseudocode**

def calculate_investment_distributions(return_event):  
owners = get_active_owners(return_event.investment)  
rows = \[\]  
<br/>for owner in owners:  
amount = return_event.net_amount \* owner.ownership_percent / 100  
rows.append(create_distribution_row(return_event, owner, amount))  
<br/>return rows

**E. Payout Integration**

Paid distributions should be executed through the Disbursements module and linked back to Chama Investment Distribution.

**4.10.11 EXIT AND LIQUIDITY POLICY ENGINE**

This is critical for member exit handling.

**A. Supported Policies**

| **Policy** | **Meaning** |
| --- | --- |
| Hold | exiting member’s investment entitlement is not paid until realization/liquidity event |
| Payout If Realized | only realized return component is payable |
| Transfer Units | member’s units/ownership must be transferred/reassigned |
| Manual | committee/manual settlement process |

**B. Exit Implication**

When a member initiates exit:

- the system must fetch active investment ownership
- compute current entitlement
- apply liquidity policy
- pass output into Member Settlement

**C. Example Behavior**

- if policy = Hold → entitlement displayed, payout = 0 now, recorded as pending or excluded
- if policy = Transfer Units → block exit until reassignment
- if policy = Manual → settlement requires explicit committee handling

**4.10.12 ACTION DEFINITIONS**

**A. Create Investment Proposal**

**Input**

{  
"chama": "CH-0001",  
"title": "Acquire Plot 17A",  
"investment_type": "LAND",  
"proposal_description": "Purchase of Plot 17A for long-term appreciation",  
"estimated_cost": 500000,  
"ownership_model": "CONTRIBUTION",  
"proposed_funding_source": "Special Levy"  
}

**Process**

1.  validate fields
2.  create proposal in Draft
3.  route for approval if submitted

**Output**

{  
"status": "success",  
"data": {  
"proposal_id": "INP-0003",  
"status": "Draft"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| IV001 | Estimated cost must be greater than zero |
| IV002 | Ownership model invalid |
| IV003 | Chama inactive |

**B. Convert Approved Proposal to Investment**

**Input**

{  
"proposal_id": "INP-0003",  
"acquisition_date": "2026-06-01",  
"acquisition_cost": 495000,  
"asset_identifier": "TitleRef-17A"  
}

**Process**

- verify proposal approved
- create investment
- set initial status Draft or Active depending on readiness
- link proposal source

**Output**

{  
"status": "success",  
"data": {  
"investment_id": "INV-0005",  
"status": "Draft"  
},  
"errors": \[\]  
}

**C. Allocate Ownership**

**Input**

{  
"investment_id": "INV-0005",  
"ownership_rows": \[  
{  
"member": "MB-0001",  
"contributed_amount": 100000  
},  
{  
"member": "MB-0002",  
"contributed_amount": 200000  
}  
\]  
}

**Process**

- validate members belong to Chama
- validate ownership model inputs
- compute percentages
- store ownership rows
- optionally lock ownership

**Output**

{  
"status": "success",  
"data": {  
"investment_id": "INV-0005",  
"ownership_model": "CONTRIBUTION",  
"owners_count": 2  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| IV101 | Ownership rows invalid |
| IV102 | Total contribution basis cannot be zero |
| IV103 | Member does not belong to this Chama |

**D. Submit Valuation**

**Input**

{  
"investment": "INV-0005",  
"valuation_date": "2026-12-31",  
"valuation_amount": 550000,  
"valuation_method": "Market Estimate",  
"valuation_basis_note": "Comparable land sales in area"  
}

**Process**

- create valuation Draft/Submitted
- route for approval if required

**Output**

{  
"status": "success",  
"data": {  
"valuation_id": "VAL-0002",  
"status": "Submitted"  
},  
"errors": \[\]  
}

**E. Record Return Event**

**Input**

{  
"investment": "INV-0005",  
"return_type": "Rent",  
"event_date": "2026-08-31",  
"gross_amount": 20000,  
"expenses_deducted": 5000,  
"realization_type": "Cash Realized"  
}

**Process**

- compute net_amount
- create return event
- calculate distribution rows if policy says immediate distribution

**Output**

{  
"status": "success",  
"data": {  
"return_event_id": "IRE-0004",  
"net_amount": 15000,  
"distribution_status": "Undistributed"  
},  
"errors": \[\]  
}

**F. Distribute Returns**

**Input**

{  
"return_event_id": "IRE-0004"  
}

**Process**

- generate per-member distribution rows
- optionally create disbursement requests/executions
- update return event distribution status

**Output**

{  
"status": "success",  
"data": {  
"return_event_id": "IRE-0004",  
"distribution_rows_created": 12  
},  
"errors": \[\]  
}

**4.10.13 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Investment List (Desk/Web)**

**Columns**

- Investment ID
- Title
- Type
- Status
- Acquisition Cost
- Current Valuation
- Unrealized Gain/Loss
- Ownership Model

**Filters**

- Chama
- Type
- Status
- Acquisition Date
- Has Returns
- Has Valuation Update

**Actions**

- New Proposal
- Open
- Create Valuation
- Record Return
- View Ownership
- Close Investment

**B. Screen: Investment Detail (Desk)**

**Sections**

**1\. Header**

| **Field** | **Type** |
| --- | --- |
| title | Data |
| investment_type | Select |
| status | Badge |
| acquisition_date | Date |
| acquisition_cost | Currency |
| current_valuation | Currency |
| total_realized_returns | Currency |
| total_unrealized_gain_loss | Currency |

**2\. Ownership Panel**

| **Field** | **Type** |
| --- | --- |
| member | Link |
| ownership_percent | Percent |
| ownership_units | Float |
| contributed_amount | Currency |
| current_entitlement_value | Currency |

**3\. Funding Panel**

- source rows with amount and date

**4\. Valuation History**

- valuation date
- amount
- method
- status

**5\. Return Events**

- event date
- type
- net amount
- distribution status

**6\. Actions**

- Allocate Ownership
- Lock Ownership
- Submit Valuation
- Record Return
- View Distribution
- Close Investment

**C. Screen: Investment Proposal (Desk)**

**Fields**

- title
- type
- description
- estimated_cost
- ownership_model
- proposed_funding_source
- linked_budget
- notes

**Actions**

- Save Draft
- Submit for Approval
- Cancel
- Convert After Approval

**D. Screen: Member Investment View (Mobile)**

**Display**

- active investments
- ownership %
- current entitlement value
- realized returns received
- investment status

**Actions**

- View details
- View valuation history summary
- View returns history

Members do not edit ownership or valuations.

**E. Screen: Valuation Review Screen (Desk)**

**Fields**

- valuation_date
- valuation_amount
- valuation_method
- valuation_basis_note
- status

**Actions**

- Submit
- Approve
- Reject
- Apply

**4.10.14 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View active investments | Yes | Yes | Yes | Yes | Yes | Yes |
| Create investment proposal | No  | Yes | No  | Limited | No  | Yes |
| Approve investment proposal | No  | No  | Yes | No  | No  | Yes |
| Convert proposal to investment | No  | Yes | Yes | No  | No  | Yes |
| Allocate ownership | No  | Yes | No  | No  | No  | Yes |
| Lock ownership | No  | Yes | Yes | No  | No  | Yes |
| Submit valuation | No  | Yes | No  | No  | No  | Yes |
| Approve valuation | No  | No  | Yes | No  | No  | Yes |
| Record return event | No  | Yes | No  | No  | No  | Yes |
| Distribute returns | No  | Yes | Yes | No  | No  | Yes |
| View all distributions | No  | Yes | Yes | No  | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Investment | current_valuation | Read | Read/Write via approved valuation flow | Read | Read |
| Ownership | ownership_percent | Read own or full if transparency policy | Read/Write | Read | Read |
| Return Event | net_amount | Read if visible summary | Read/Write | Read | Read |
| Distribution | distribution_amount | Read own | Read | Read | Read |

**C. Transparency Note**

Depending on Chama policy, members may:

- see only their own ownership row
- or see full ownership table  
    This should be configurable.

**D. Chama Scope Rule**

All investment-related records must be filtered by:

doc.chama == current_user_selected_chama

**4.10.15 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| investment_proposed | submit proposal | approvers / members if governance model says so | APP | investment_proposed | Medium |
| investment_approved | proposal approved | treasurer/chair/members | APP | investment_approved | Medium |
| investment_rejected | proposal rejected | proposer | APP | investment_rejected | Medium |
| valuation_submitted | submit valuation | approver | APP | valuation_submitted | Medium |
| valuation_applied | apply valuation | members / officials | APP | valuation_applied | Medium |
| return_event_recorded | return saved | treasurer/chair | APP | return_event_recorded | Medium |
| returns_distributed | distribution executed | recipient members | APP, SMS optional | returns_distributed | Medium |
| investment_closed | status -> Closed | members / officials | APP | investment_closed | Medium |

**Example Template: returns_distributed**

A return of {distribution_amount} from investment "{investment_title}" has been distributed to you.

**Example Template: valuation_applied**

The valuation of investment "{investment_title}" has been updated to {valuation_amount}.

**4.10.16 API ENDPOINTS (FULL)**

**A. Create Investment Proposal**

POST /api/method/chama.investment.create_proposal

**B. Submit Investment Proposal**

POST /api/method/chama.investment.submit_proposal

**C. Convert Proposal to Investment**

POST /api/method/chama.investment.convert_proposal

**D. Allocate Ownership**

POST /api/method/chama.investment.allocate_ownership

**E. Get Investment Detail**

GET /api/method/chama.investment.detail?investment=INV-0005

**F. Submit Valuation**

POST /api/method/chama.investment.submit_valuation

**G. Approve / Apply Valuation**

POST /api/method/chama.investment.apply_valuation

**H. Record Return Event**

POST /api/method/chama.investment.record_return

**I. Distribute Returns**

POST /api/method/chama.investment.distribute_returns

**Example Response**

{  
"status": "success",  
"data": {  
"investment_id": "INV-0005",  
"status": "Active",  
"current_valuation": 550000,  
"owners_count": 12  
},  
"errors": \[\]  
}

**4.10.17 REPORTS**

**A. Investment Register**

**Columns**

- Investment ID
- Title
- Type
- Status
- Acquisition Cost
- Current Valuation
- Unrealized Gain/Loss

**B. Ownership Allocation Report**

**Columns**

- Investment
- Member
- Ownership %
- Ownership Units
- Contributed Amount
- Current Entitlement Value

**C. Valuation History Report**

**Columns**

- Investment
- Valuation Date
- Amount
- Method
- Status
- Applied

**D. Investment Returns Report**

**Columns**

- Investment
- Event Date
- Return Type
- Gross Amount
- Net Amount
- Distribution Status

**E. Member Investment Entitlement Report**

**Columns**

- Member
- Investment
- Ownership %
- Current Entitlement
- Returns Paid

**4.10.18 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Investment Proposal | Required |
| Custom DocType | Chama Investment | Required |
| Child Table | Chama Investment Funding | Required |
| Child Table | Chama Investment Ownership | Required |
| Custom DocType | Chama Investment Valuation | Required |
| Custom DocType | Chama Investment Return Event | Required |
| Custom DocType | Chama Investment Distribution | Required |
| Reports | register / ownership / valuation / returns / entitlements | Required |
| Notifications | proposal / valuation / returns / closure | Required |
| Integration | Budget / Proposal / Disbursement / Member Settlement | Required |

**4.10.19 WORKFLOW CONFIGURATION**

**Workflow Name: Investment Proposal Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Pending Approval | under governance |
| Approved | ready for conversion |
| Rejected | declined |
| Cancelled | terminated |
| Converted | active investment created |

**Workflow Name: Investment Valuation Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Submitted | awaiting review |
| Approved | accepted |
| Rejected | declined |
| Applied | current valuation updated |
| Cancelled | terminated |

**4.10.20 SERVER LOGIC / HOOKS**

**A. Recalculate Entitlements**

def refresh_owner_entitlements(investment):  
owners = get_active_owners(investment)  
for owner in owners:  
owner.current_entitlement_value = investment.current_valuation \* owner.ownership_percent / 100  
owner.save()

**B. Apply Valuation**

def apply_valuation(valuation):  
ensure_status(valuation, "Approved")  
inv = frappe.get_doc("Chama Investment", valuation.investment)  
inv.current_valuation = valuation.valuation_amount  
inv.total_unrealized_gain_loss = inv.current_valuation - inv.acquisition_cost  
inv.save()  
refresh_owner_entitlements(inv)  
valuation.status = "Applied"  
valuation.save()

**C. Record Return Event**

def record_return_event(data):  
net = data\["gross_amount"\] - data.get("expenses_deducted", 0)  
event = frappe.get_doc({  
"doctype": "Chama Investment Return Event",  
\*\*data,  
"net_amount": net,  
"distribution_status": "Undistributed"  
}).insert()  
return event

**D. Distribute Returns**

def distribute_returns(return_event):  
rows = calculate_investment_distributions(return_event)  
for row in rows:  
row.save()  
update_return_distribution_status(return_event)

**4.10.21 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Ownership totals not 100% | validation on save | block percentage-based model | Yes |
| Member exits while investment active | exit flow detects active ownership | apply liquidity policy | Yes |
| Negative valuation change | valuation < acquisition / prior value | allow, show loss clearly | Yes |
| Return event with zero or negative net amount | gross - expenses <= 0 | block or hold as configured | Yes |
| Proposal approved but acquisition not completed | no conversion | keep approved proposal pending conversion/cancel | Yes |
| Partial sale | realization event flagged partial | move status to Partially Realized | Yes |
| Revaluation after closure | status closed | block | Yes |
| Ownership change after lock | locked flag true | require amendment/override | Yes |

**4.10.22 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | investment funding may come from member contributions or levies |
| Disbursements | acquisition outflows and return payouts link here |
| Budgeting | investment purchase may require budget allocation |
| Meetings / Voting | proposals and major changes may require governance approval |
| Member Lifecycle | exits and settlements must consider ownership and liquidity policy |
| Reconciliation | realized returns and acquisition outflows affect expected balances |
| Analytics | portfolio value, ROI, and entitlement metrics consume investment data |

**4.10.23 CRITICAL IMPLEMENTATION RULES**

- No active investment may exist without chama, type, ownership_model, acquisition_date, and acquisition_cost
- Ownership allocations must always be reconstructible and auditable
- Current valuation may only be changed through approved valuation workflow
- Return distributions must be derived from snapshotted ownership at event time
- Investment exit/liquidity policy must be explicit and must feed member settlement
- Every investment-related record must include chama
- Closed investments must be read-only except for historical reporting
- Distribution amounts shown to members must match stored distribution records exactly

## MODULE 4.10 — INVESTMENT MANAGEMENT

**4.10.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Investment master record | Custom |
| Funding linkage | Custom + Contributions / Disbursements integrations |
| Ownership allocation | Custom |
| Valuation history | Custom |
| Return distribution | Custom + Disbursements module |
| Governance approval | Voting & Resolutions / Meetings |
| Member exit implications | Member Lifecycle + Settlement |
| Reporting and dashboards | ERPNext reports + custom logic |

**4.10.2 MODULE PURPOSE**

The Investment Management module shall manage:

- creation of investment proposals
- approval of investments before activation
- recording of acquired assets
- classification of investment types
- tracking of how investments were funded
- ownership allocation among members
- changes in valuation over time
- recording of returns generated by investments
- return distribution to members
- partial sale or closure of investments
- member exit treatment where investments remain open or illiquid

This module must explicitly separate:

1.  **Investment Proposal**  
    the planned asset or venture before acquisition
2.  **Investment Record**  
    the active investment after approval/acquisition
3.  **Funding Record**  
    how the investment was financed
4.  **Ownership Allocation**  
    the entitlement of members in the investment
5.  **Valuation Record**  
    the periodic estimate or measured value of the investment
6.  **Return Event**  
    income or realized proceeds from the investment

That separation is mandatory.

**4.10.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall be primarily custom because ERPNext does not natively model Chama-style pooled ownership and member-linked investment entitlements in the exact way needed.

**Reuse from ERPNext / Frappe**

- DocTypes and child tables
- attachments
- workflows where useful
- reports and dashboards
- roles and permissions
- audit/version patterns

**Custom Chama layer**

- investment proposal and approval flow
- active investment records
- ownership allocation engine
- valuation history
- return generation and distribution logic
- exit entitlement and liquidity policy handling
- cross-linkage to budgets, meetings, and resolutions

**Rule**

Do not reduce investment management to a single ledger line or generic asset row.  
A Chama investment is both:

- a financial asset
- a social ownership construct

Both sides must be modeled.

**4.10.4 INVESTMENT TYPES**

The system shall support normalized investment types:

| **Type Code** | **Label** | **Description** |
| --- | --- | --- |
| LAND | Land / Plot | land parcels and property purchase |
| BUSINESS | Business Venture | shops, farms, ventures, partnerships |
| FIN_ASSET | Financial Asset | stocks, bonds, unit trusts, fixed-income placements |
| EQUIPMENT | Equipment / Machinery | productive assets |
| PROPERTY | Rental / Property Asset | property producing rent or occupancy value |
| LIVESTOCK | Livestock / Agricultural Asset | livestock, farming assets |
| OTHER | Other Investment | configured catch-all |

**4.10.5 OWNERSHIP MODELS**

The system shall support at least the following ownership models:

| **Model Code** | **Label** | **Description** |
| --- | --- | --- |
| EQUAL | Equal Ownership | all eligible members share equally |
| CONTRIBUTION | Contribution-Based | ownership proportional to funding contribution |
| HYBRID | Hybrid | equal base plus weighted component |
| UNITIZED | Unit-Based | ownership tracked in units purchased |
| MANUAL | Manual Allocation | explicit admin-defined allocation with audit |

**4.10.6 DATA MODEL (FULL)**

**A. DocType: Chama Investment Proposal**

**Purpose**

Represents an investment idea/proposal before acquisition or activation.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Proposal ID | Data (Auto) | Yes | Example INP-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| title | Title | Data | Yes |     |
| investment_type | Select | Yes | from investment types |     |
| proposal_description | Long Text | Yes |     |     |
| estimated_cost | Currency | Yes |     |     |
| proposed_acquisition_date | Date | No  |     |     |
| ownership_model | Select | Yes | from ownership models |     |
| proposed_funding_source | Select | No  | Contributions / Levy / Reserve / Mixed / External |     |
| linked_budget | Link(Chama Budget) | No  | if budget-backed |     |
| approval_proposal | Link(Chama Proposal) | No  | governance vote linkage |     |
| status | Select | Yes | Draft / Pending Approval / Approved / Rejected / Cancelled / Converted |     |
| created_by | Link(User) | Yes |     |     |
| notes | Small Text | No  |     |     |

**Status Enum**

Draft  
Pending Approval  
Approved  
Rejected  
Cancelled  
Converted

**B. DocType: Chama Investment**

**Purpose**

Represents an approved/active investment asset or venture.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Investment ID | Data (Auto) | Yes | Example INV-0001 |
| chama | Chama | Link(Chama) | Yes | Tenant anchor |
| title | Title | Data | Yes |     |
| investment_type | Select | Yes |     |     |
| ownership_model | Select | Yes |     |     |
| acquisition_date | Date | Yes |     |     |
| acquisition_cost | Currency | Yes |     |     |
| currency | Link(Currency) | Yes |     |     |
| status | Select | Yes | Draft / Active / Partially Realized / Closed / Cancelled |     |
| proposal_source | Link(Chama Investment Proposal) | No  | original proposal |     |
| linked_budget | Link(Chama Budget) | No  | if acquired under budget |     |
| linked_disbursement_execution | Link(Chama Disbursement Execution) | No  | acquisition payout |     |
| asset_description | Long Text | No  |     |     |
| asset_identifier | Data | No  | title number / account number / asset code |     |
| ownership_locked | Check | Yes | 0/1 | whether allocation locked after acquisition |
| current_valuation | Currency | Yes | latest computed/approved valuation |     |
| total_realized_returns | Currency | Yes | cumulative |     |
| total_unrealized_gain_loss | Currency | Yes | current_valuation - acquisition_cost |     |
| exit_liquidity_policy | Select | Yes | Hold / Payout If Realized / Transfer Units / Manual |     |
| created_by | Link(User) | Yes |     |     |
| created_on | Datetime | Yes |     |     |

**Status Enum**

Draft  
Active  
Partially Realized  
Closed  
Cancelled

**Computed Rule**

total_unrealized_gain_loss = current_valuation - acquisition_cost

**C. Child Table: Chama Investment Funding**

**Parent**

Chama Investment

**Purpose**

Breaks down how the investment was financed.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| funding_type | Select | Yes | Contribution / Special Levy / Reserve / External / Mixed |     |
| source_reference | Data / Dynamic Link | No  | contribution batch / budget / disbursement |     |
| amount | Currency | Yes |     |     |
| funding_date | Date | No  |     |     |
| notes | Small Text | No  |     |     |

**D. Child Table: Chama Investment Ownership**

**Parent**

Chama Investment

**Purpose**

Represents each member’s ownership allocation.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| member | Link(Chama Member) | Yes | owner member |     |
| ownership_percent | Percent | No  | used in percentage models |     |
| ownership_units | Float | No  | used in unitized models |     |
| contributed_amount | Currency | No  | contribution basis |     |
| current_entitlement_value | Currency | Yes | computed |     |
| active | Check | Yes | 1/0 |     |
| notes | Small Text | No  |     |     |

**Constraints**

- total ownership must satisfy model-specific rules
- for percentage models, total active ownership should = 100%
- for unitized models, percentages may be derived

**E. DocType: Chama Investment Valuation**

**Purpose**

Stores one valuation event.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Valuation ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| investment | Link(Chama Investment) | Yes |     |
| valuation_date | Date | Yes |     |
| valuation_amount | Currency | Yes |     |
| valuation_method | Select | Yes |     |
| valuation_basis_note | Small Text | Yes |     |
| prepared_by | Link(User) | Yes |     |
| approved_by | Link(User) | No  |     |
| status | Select | Yes |     |

**Valuation Methods**

- Market Estimate
- External Appraisal
- Book Value
- Income-Based
- Manual Committee Assessment

**Status Enum**

Draft  
Submitted  
Approved  
Rejected  
Applied  
Cancelled

**Rule**

Only one valuation may be the active current valuation at a time after approval/application.

**F. DocType: Chama Investment Return Event**

**Purpose**

Represents income or realized return generated by an investment.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Return Event ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| investment | Link(Chama Investment) | Yes |     |
| return_type | Select | Yes |     |
| event_date | Date | Yes |     |
| gross_amount | Currency | Yes |     |
| expenses_deducted | Currency | Yes |     |
| net_amount | Currency | Yes |     |
| realization_type | Select | Yes |     |
| distribution_status | Select | Yes |     |
| linked_disbursement_batch_ref | Data | No  |     |
| notes | Small Text | No  |     |

**Return Types**

- Rent
- Profit Share
- Dividend
- Sale Proceeds
- Interest
- Other

**Realization Types**

- Cash Realized
- Book Adjustment
- Partial Realization
- Full Exit

**Distribution Status Enum**

Undistributed  
Partially Distributed  
Distributed  
Held  
Cancelled

**Computed Rule**

net_amount = gross_amount - expenses_deducted

**G. DocType: Chama Investment Distribution**

**Purpose**

Stores per-member distribution generated from a return event.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Distribution ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| return_event | Link(Chama Investment Return Event) | Yes |     |
| investment | Link(Chama Investment) | Yes |     |
| member | Link(Chama Member) | Yes |     |
| ownership_basis_snapshot | Float / JSON | Yes |     |
| distribution_amount | Currency | Yes |     |
| distribution_status | Select | Yes |     |
| linked_disbursement_execution | Link(Chama Disbursement Execution) | No  |     |
| notes | Small Text | No  |     |

**Distribution Status Enum**

Calculated  
Approved  
Paid  
Held  
Cancelled

**4.10.7 STATE MACHINES (FORMAL)**

**A. Investment Proposal State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Pending Approval | Submit | Treasurer/Secretary | valid fields | create governance proposal if needed |
| Pending Approval | Approved | Approval result | System/Chair | resolution approved | allow conversion |
| Pending Approval | Rejected | Approval result | System/Chair | resolution rejected | notify proposer |
| Draft / Pending Approval | Cancelled | Cancel | Creator/Admin | not converted | log |
| Approved | Converted | Convert to investment | Treasurer/Admin | acquisition details complete | create investment record |

**B. Investment State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Active | Activate | Treasurer/Admin | acquisition completed, ownership set | initialize valuation |
| Active | Partially Realized | partial sale/realization | Treasurer/Admin | realization event recorded | update returns/liquidity |
| Active / Partially Realized | Closed | full disposal / closure | Treasurer/Admin | no remaining ownership or asset closed | finalize |
| Draft | Cancelled | Cancel | Admin | not active | log |

**C. Valuation State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Draft | Submitted | Submit | Treasurer/Reviewer | note present | notify approver |
| Submitted | Approved | Approve | Chair/Authorized reviewer | valid valuation | ready to apply |
| Submitted | Rejected | Reject | Reviewer | —   | notify preparer |
| Approved | Applied | Apply | System/Treasurer | investment active | update current valuation |
| Draft / Submitted | Cancelled | Cancel | Creator/Admin | not applied | log |

**D. Return Event State Machine**

| **From** | **To** | **Trigger** | **Actor** | **Conditions** | **Side Effects** |
| --- | --- | --- | --- | --- | --- |
| Created | Undistributed | Save event | Treasurer | net amount valid | ready for calculation |
| Undistributed | Partially Distributed | some distributions paid | System | partial payout state | update |
| Undistributed / Partially Distributed | Distributed | all distributions paid | System | all linked payouts done | update cumulative totals |
| Any prefinal | Held | hold decision | Treasurer/Chair | policy reason | no payout |
| Any prefinal | Cancelled | cancel | Admin | invalid event | reverse implications if needed |

**4.10.8 OWNERSHIP ALLOCATION ENGINE**

This is central and must be precise.

**A. Equal Ownership**

ownership_percent = 100 / number_of_active_owners

**B. Contribution-Based Ownership**

ownership_percent =  
member_contributed_amount / total_contributed_amount \* 100

**C. Unitized Ownership**

ownership_percent =  
member_units / total_units \* 100

**D. Hybrid Ownership**

Hybrid formula must be explicitly configured. Example:

ownership_percent =  
(0.5 \* equal_share_component) + (0.5 \* contribution_weight_component)

**E. Pseudocode**

def recalculate_investment_ownership(investment):  
owners = get_active_owners(investment)  
<br/>if investment.ownership_model == "EQUAL":  
pct = 100 / len(owners) if owners else 0  
for o in owners:  
o.ownership_percent = pct  
<br/>elif investment.ownership_model == "CONTRIBUTION":  
total = sum(o.contributed_amount for o in owners)  
for o in owners:  
o.ownership_percent = (o.contributed_amount / total \* 100) if total else 0  
<br/>elif investment.ownership_model == "UNITIZED":  
total_units = sum(o.ownership_units for o in owners)  
for o in owners:  
o.ownership_percent = (o.ownership_units / total_units \* 100) if total_units else 0  
<br/>save_all(owners)

**F. Validation Rules**

- for percentage-based models, total active ownership must equal 100% within rounding tolerance
- for equal model, manual override not allowed unless policy enables
- ownership changes after lock require amendment trail

**4.10.9 VALUATION ENGINE**

**A. Current Valuation Update Rule**

Only an Approved + Applied valuation updates current_valuation.

**B. Unrealized Gain/Loss Formula**

unrealized_gain_loss = current_valuation - acquisition_cost

**C. Member Entitlement Value**

member_entitlement_value =  
current_valuation \* ownership_percent / 100

**D. Pseudocode**

def apply_investment_valuation(valuation):  
ensure_valuation_approved(valuation)  
inv = frappe.get_doc("Chama Investment", valuation.investment)  
inv.current_valuation = valuation.valuation_amount  
inv.total_unrealized_gain_loss = inv.current_valuation - inv.acquisition_cost  
inv.save()  
refresh_owner_entitlements(inv)

**4.10.10 RETURN DISTRIBUTION ENGINE**

**A. Distribution Basis**

By default, return distributions are allocated using ownership snapshot at event date.

**B. Formula**

distribution_amount =  
return_event.net_amount \* member_ownership_percent / 100

**C. Held Returns**

Where policy requires retention or reserve:

- return event may remain Held
- no distribution rows are paid until approved

**D. Pseudocode**

def calculate_investment_distributions(return_event):  
owners = get_active_owners(return_event.investment)  
rows = \[\]  
<br/>for owner in owners:  
amount = return_event.net_amount \* owner.ownership_percent / 100  
rows.append(create_distribution_row(return_event, owner, amount))  
<br/>return rows

**E. Payout Integration**

Paid distributions should be executed through the Disbursements module and linked back to Chama Investment Distribution.

**4.10.11 EXIT AND LIQUIDITY POLICY ENGINE**

This is critical for member exit handling.

**A. Supported Policies**

| **Policy** | **Meaning** |
| --- | --- |
| Hold | exiting member’s investment entitlement is not paid until realization/liquidity event |
| Payout If Realized | only realized return component is payable |
| Transfer Units | member’s units/ownership must be transferred/reassigned |
| Manual | committee/manual settlement process |

**B. Exit Implication**

When a member initiates exit:

- the system must fetch active investment ownership
- compute current entitlement
- apply liquidity policy
- pass output into Member Settlement

**C. Example Behavior**

- if policy = Hold → entitlement displayed, payout = 0 now, recorded as pending or excluded
- if policy = Transfer Units → block exit until reassignment
- if policy = Manual → settlement requires explicit committee handling

**4.10.12 ACTION DEFINITIONS**

**A. Create Investment Proposal**

**Input**

{  
"chama": "CH-0001",  
"title": "Acquire Plot 17A",  
"investment_type": "LAND",  
"proposal_description": "Purchase of Plot 17A for long-term appreciation",  
"estimated_cost": 500000,  
"ownership_model": "CONTRIBUTION",  
"proposed_funding_source": "Special Levy"  
}

**Process**

1.  validate fields
2.  create proposal in Draft
3.  route for approval if submitted

**Output**

{  
"status": "success",  
"data": {  
"proposal_id": "INP-0003",  
"status": "Draft"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| IV001 | Estimated cost must be greater than zero |
| IV002 | Ownership model invalid |
| IV003 | Chama inactive |

**B. Convert Approved Proposal to Investment**

**Input**

{  
"proposal_id": "INP-0003",  
"acquisition_date": "2026-06-01",  
"acquisition_cost": 495000,  
"asset_identifier": "TitleRef-17A"  
}

**Process**

- verify proposal approved
- create investment
- set initial status Draft or Active depending on readiness
- link proposal source

**Output**

{  
"status": "success",  
"data": {  
"investment_id": "INV-0005",  
"status": "Draft"  
},  
"errors": \[\]  
}

**C. Allocate Ownership**

**Input**

{  
"investment_id": "INV-0005",  
"ownership_rows": \[  
{  
"member": "MB-0001",  
"contributed_amount": 100000  
},  
{  
"member": "MB-0002",  
"contributed_amount": 200000  
}  
\]  
}

**Process**

- validate members belong to Chama
- validate ownership model inputs
- compute percentages
- store ownership rows
- optionally lock ownership

**Output**

{  
"status": "success",  
"data": {  
"investment_id": "INV-0005",  
"ownership_model": "CONTRIBUTION",  
"owners_count": 2  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| IV101 | Ownership rows invalid |
| IV102 | Total contribution basis cannot be zero |
| IV103 | Member does not belong to this Chama |

**D. Submit Valuation**

**Input**

{  
"investment": "INV-0005",  
"valuation_date": "2026-12-31",  
"valuation_amount": 550000,  
"valuation_method": "Market Estimate",  
"valuation_basis_note": "Comparable land sales in area"  
}

**Process**

- create valuation Draft/Submitted
- route for approval if required

**Output**

{  
"status": "success",  
"data": {  
"valuation_id": "VAL-0002",  
"status": "Submitted"  
},  
"errors": \[\]  
}

**E. Record Return Event**

**Input**

{  
"investment": "INV-0005",  
"return_type": "Rent",  
"event_date": "2026-08-31",  
"gross_amount": 20000,  
"expenses_deducted": 5000,  
"realization_type": "Cash Realized"  
}

**Process**

- compute net_amount
- create return event
- calculate distribution rows if policy says immediate distribution

**Output**

{  
"status": "success",  
"data": {  
"return_event_id": "IRE-0004",  
"net_amount": 15000,  
"distribution_status": "Undistributed"  
},  
"errors": \[\]  
}

**F. Distribute Returns**

**Input**

{  
"return_event_id": "IRE-0004"  
}

**Process**

- generate per-member distribution rows
- optionally create disbursement requests/executions
- update return event distribution status

**Output**

{  
"status": "success",  
"data": {  
"return_event_id": "IRE-0004",  
"distribution_rows_created": 12  
},  
"errors": \[\]  
}

**4.10.13 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Investment List (Desk/Web)**

**Columns**

- Investment ID
- Title
- Type
- Status
- Acquisition Cost
- Current Valuation
- Unrealized Gain/Loss
- Ownership Model

**Filters**

- Chama
- Type
- Status
- Acquisition Date
- Has Returns
- Has Valuation Update

**Actions**

- New Proposal
- Open
- Create Valuation
- Record Return
- View Ownership
- Close Investment

**B. Screen: Investment Detail (Desk)**

**Sections**

**1\. Header**

| **Field** | **Type** |
| --- | --- |
| title | Data |
| investment_type | Select |
| status | Badge |
| acquisition_date | Date |
| acquisition_cost | Currency |
| current_valuation | Currency |
| total_realized_returns | Currency |
| total_unrealized_gain_loss | Currency |

**2\. Ownership Panel**

| **Field** | **Type** |
| --- | --- |
| member | Link |
| ownership_percent | Percent |
| ownership_units | Float |
| contributed_amount | Currency |
| current_entitlement_value | Currency |

**3\. Funding Panel**

- source rows with amount and date

**4\. Valuation History**

- valuation date
- amount
- method
- status

**5\. Return Events**

- event date
- type
- net amount
- distribution status

**6\. Actions**

- Allocate Ownership
- Lock Ownership
- Submit Valuation
- Record Return
- View Distribution
- Close Investment

**C. Screen: Investment Proposal (Desk)**

**Fields**

- title
- type
- description
- estimated_cost
- ownership_model
- proposed_funding_source
- linked_budget
- notes

**Actions**

- Save Draft
- Submit for Approval
- Cancel
- Convert After Approval

**D. Screen: Member Investment View (Mobile)**

**Display**

- active investments
- ownership %
- current entitlement value
- realized returns received
- investment status

**Actions**

- View details
- View valuation history summary
- View returns history

Members do not edit ownership or valuations.

**E. Screen: Valuation Review Screen (Desk)**

**Fields**

- valuation_date
- valuation_amount
- valuation_method
- valuation_basis_note
- status

**Actions**

- Submit
- Approve
- Reject
- Apply

**4.10.14 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** |
| --- | --- | --- | --- | --- | --- | --- |
| View active investments | Yes | Yes | Yes | Yes | Yes | Yes |
| Create investment proposal | No  | Yes | No  | Limited | No  | Yes |
| Approve investment proposal | No  | No  | Yes | No  | No  | Yes |
| Convert proposal to investment | No  | Yes | Yes | No  | No  | Yes |
| Allocate ownership | No  | Yes | No  | No  | No  | Yes |
| Lock ownership | No  | Yes | Yes | No  | No  | Yes |
| Submit valuation | No  | Yes | No  | No  | No  | Yes |
| Approve valuation | No  | No  | Yes | No  | No  | Yes |
| Record return event | No  | Yes | No  | No  | No  | Yes |
| Distribute returns | No  | Yes | Yes | No  | No  | Yes |
| View all distributions | No  | Yes | Yes | No  | Yes | Yes |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Treasurer** | **Chair** | **Auditor** |
| --- | --- | --- | --- | --- | --- |
| Investment | current_valuation | Read | Read/Write via approved valuation flow | Read | Read |
| Ownership | ownership_percent | Read own or full if transparency policy | Read/Write | Read | Read |
| Return Event | net_amount | Read if visible summary | Read/Write | Read | Read |
| Distribution | distribution_amount | Read own | Read | Read | Read |

**C. Transparency Note**

Depending on Chama policy, members may:

- see only their own ownership row
- or see full ownership table  
    This should be configurable.

**D. Chama Scope Rule**

All investment-related records must be filtered by:

doc.chama == current_user_selected_chama

**4.10.15 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| investment_proposed | submit proposal | approvers / members if governance model says so | APP | investment_proposed | Medium |
| investment_approved | proposal approved | treasurer/chair/members | APP | investment_approved | Medium |
| investment_rejected | proposal rejected | proposer | APP | investment_rejected | Medium |
| valuation_submitted | submit valuation | approver | APP | valuation_submitted | Medium |
| valuation_applied | apply valuation | members / officials | APP | valuation_applied | Medium |
| return_event_recorded | return saved | treasurer/chair | APP | return_event_recorded | Medium |
| returns_distributed | distribution executed | recipient members | APP, SMS optional | returns_distributed | Medium |
| investment_closed | status -> Closed | members / officials | APP | investment_closed | Medium |

**Example Template: returns_distributed**

A return of {distribution_amount} from investment "{investment_title}" has been distributed to you.

**Example Template: valuation_applied**

The valuation of investment "{investment_title}" has been updated to {valuation_amount}.

**4.10.16 API ENDPOINTS (FULL)**

**A. Create Investment Proposal**

POST /api/method/chama.investment.create_proposal

**B. Submit Investment Proposal**

POST /api/method/chama.investment.submit_proposal

**C. Convert Proposal to Investment**

POST /api/method/chama.investment.convert_proposal

**D. Allocate Ownership**

POST /api/method/chama.investment.allocate_ownership

**E. Get Investment Detail**

GET /api/method/chama.investment.detail?investment=INV-0005

**F. Submit Valuation**

POST /api/method/chama.investment.submit_valuation

**G. Approve / Apply Valuation**

POST /api/method/chama.investment.apply_valuation

**H. Record Return Event**

POST /api/method/chama.investment.record_return

**I. Distribute Returns**

POST /api/method/chama.investment.distribute_returns

**Example Response**

{  
"status": "success",  
"data": {  
"investment_id": "INV-0005",  
"status": "Active",  
"current_valuation": 550000,  
"owners_count": 12  
},  
"errors": \[\]  
}

**4.10.17 REPORTS**

**A. Investment Register**

**Columns**

- Investment ID
- Title
- Type
- Status
- Acquisition Cost
- Current Valuation
- Unrealized Gain/Loss

**B. Ownership Allocation Report**

**Columns**

- Investment
- Member
- Ownership %
- Ownership Units
- Contributed Amount
- Current Entitlement Value

**C. Valuation History Report**

**Columns**

- Investment
- Valuation Date
- Amount
- Method
- Status
- Applied

**D. Investment Returns Report**

**Columns**

- Investment
- Event Date
- Return Type
- Gross Amount
- Net Amount
- Distribution Status

**E. Member Investment Entitlement Report**

**Columns**

- Member
- Investment
- Ownership %
- Current Entitlement
- Returns Paid

**4.10.18 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Investment Proposal | Required |
| Custom DocType | Chama Investment | Required |
| Child Table | Chama Investment Funding | Required |
| Child Table | Chama Investment Ownership | Required |
| Custom DocType | Chama Investment Valuation | Required |
| Custom DocType | Chama Investment Return Event | Required |
| Custom DocType | Chama Investment Distribution | Required |
| Reports | register / ownership / valuation / returns / entitlements | Required |
| Notifications | proposal / valuation / returns / closure | Required |
| Integration | Budget / Proposal / Disbursement / Member Settlement | Required |

**4.10.19 WORKFLOW CONFIGURATION**

**Workflow Name: Investment Proposal Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Pending Approval | under governance |
| Approved | ready for conversion |
| Rejected | declined |
| Cancelled | terminated |
| Converted | active investment created |

**Workflow Name: Investment Valuation Approval**

| **State** | **Meaning** |
| --- | --- |
| Draft | editable |
| Submitted | awaiting review |
| Approved | accepted |
| Rejected | declined |
| Applied | current valuation updated |
| Cancelled | terminated |

**4.10.20 SERVER LOGIC / HOOKS**

**A. Recalculate Entitlements**

def refresh_owner_entitlements(investment):  
owners = get_active_owners(investment)  
for owner in owners:  
owner.current_entitlement_value = investment.current_valuation \* owner.ownership_percent / 100  
owner.save()

**B. Apply Valuation**

def apply_valuation(valuation):  
ensure_status(valuation, "Approved")  
inv = frappe.get_doc("Chama Investment", valuation.investment)  
inv.current_valuation = valuation.valuation_amount  
inv.total_unrealized_gain_loss = inv.current_valuation - inv.acquisition_cost  
inv.save()  
refresh_owner_entitlements(inv)  
valuation.status = "Applied"  
valuation.save()

**C. Record Return Event**

def record_return_event(data):  
net = data\["gross_amount"\] - data.get("expenses_deducted", 0)  
event = frappe.get_doc({  
"doctype": "Chama Investment Return Event",  
\*\*data,  
"net_amount": net,  
"distribution_status": "Undistributed"  
}).insert()  
return event

**D. Distribute Returns**

def distribute_returns(return_event):  
rows = calculate_investment_distributions(return_event)  
for row in rows:  
row.save()  
update_return_distribution_status(return_event)

**4.10.21 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Ownership totals not 100% | validation on save | block percentage-based model | Yes |
| Member exits while investment active | exit flow detects active ownership | apply liquidity policy | Yes |
| Negative valuation change | valuation < acquisition / prior value | allow, show loss clearly | Yes |
| Return event with zero or negative net amount | gross - expenses <= 0 | block or hold as configured | Yes |
| Proposal approved but acquisition not completed | no conversion | keep approved proposal pending conversion/cancel | Yes |
| Partial sale | realization event flagged partial | move status to Partially Realized | Yes |
| Revaluation after closure | status closed | block | Yes |
| Ownership change after lock | locked flag true | require amendment/override | Yes |

**4.10.22 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | investment funding may come from member contributions or levies |
| Disbursements | acquisition outflows and return payouts link here |
| Budgeting | investment purchase may require budget allocation |
| Meetings / Voting | proposals and major changes may require governance approval |
| Member Lifecycle | exits and settlements must consider ownership and liquidity policy |
| Reconciliation | realized returns and acquisition outflows affect expected balances |
| Analytics | portfolio value, ROI, and entitlement metrics consume investment data |

**4.10.23 CRITICAL IMPLEMENTATION RULES**

- No active investment may exist without chama, type, ownership_model, acquisition_date, and acquisition_cost
- Ownership allocations must always be reconstructible and auditable
- Current valuation may only be changed through approved valuation workflow
- Return distributions must be derived from snapshotted ownership at event time
- Investment exit/liquidity policy must be explicit and must feed member settlement
- Every investment-related record must include chama
- Closed investments must be read-only except for historical reporting
- Distribution amounts shown to members must match stored distribution records exactly

## MODULE 4.11 — MULTI-CHAMA / MULTI-TENANT PLATFORM CONTROLS

**4.11.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Chama tenant master record | Custom |
| Tenant scoping fields on all transactional records | Shared cross-module requirement |
| User-to-Chama membership relationship | Member Lifecycle + platform controls |
| Context switching | Custom |
| Permission scoping | ERPNext/Frappe + custom enforcement |
| Query filtering and API enforcement | Custom |
| Tenant-level settings | Custom |
| Cross-tenant administration | Admin-only custom layer |

**4.11.2 MODULE PURPOSE**

The Multi-Chama / Multi-Tenant module shall manage:

- creation and lifecycle of Chama tenants
- strict tenant isolation
- per-Chama configuration
- a user belonging to multiple Chamas
- Chama-specific roles for the same user
- Chama context switching in web and mobile
- tenant-scoped lists, reports, dashboards, and notifications
- tenant-aware API access
- cross-tenant admin support without data leakage
- archival or deactivation of Chamas without deleting their history

This module must explicitly separate:

1.  **Platform User**  
    the authentication identity
2.  **Chama Tenant**  
    the isolated operating entity
3.  **Chama Membership**  
    the user’s participation record within a tenant
4.  **Active Chama Context**  
    the current tenant lens through which data is viewed and actions are taken
5.  **Global Administration**  
    the limited platform-level ability to create/manage Chamas without bypassing audit or isolation

That separation is mandatory.

**4.11.3 CORE PLATFORM RULE**

**NON-NEGOTIABLE RULE**

Every business record in the system must be traceably owned by exactly one Chama, unless it is an explicitly global administrative/configuration record.

This means:

- loans belong to one Chama
- contributions belong to one Chama
- meetings belong to one Chama
- investments belong to one Chama
- notifications belong to one Chama
- member records belong to one Chama

Global exceptions should be rare and controlled:

- global notification templates
- platform admin configuration
- system metadata

**4.11.4 ERPNext IMPLEMENTATION STRATEGY**

This module shall use a combination of:

- custom tenant records
- user permissions
- explicit chama link fields
- session/current-context handling
- API-level enforcement
- query-level filtering
- report-level filtering

**Reuse from ERPNext / Frappe**

- User DocType
- roles and permissions
- user permissions
- session/context facilities
- list and report permissions
- DocType hooks and query filters
- workspaces and dashboards
- REST APIs

**Custom Chama layer**

- Chama tenant master
- Chama context switch model
- per-Chama role resolution
- multi-membership handling
- tenant-aware route/deep-link logic
- cross-tenant admin tooling

**Rule**

Tenant isolation must not rely only on UI hiding.  
It must be enforced at:

- data model level
- query level
- permission level
- API level
- report/export level

**4.11.5 DATA MODEL (FULL)**

**A. DocType: Chama**

**Purpose**

Represents one tenant/group in the platform.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Chama ID | Data (Auto or configured) | Yes | Example CH-0001 |
| chama_name | Chama Name | Data | Yes | human-readable name |
| chama_code | Chama Code | Data | Yes | unique short code |
| status | Select | Yes | Active / Inactive / Archived |     |
| base_currency | Link(Currency) | Yes |     |     |
| country | Data | No  |     |     |
| timezone | Data | Yes | default tenant timezone |     |
| founding_date | Date | No  |     |     |
| description | Small Text | No  |     |     |
| owner_user | Link(User) | No  | initial creating owner/admin |     |
| allow_new_member_applications | Check | Yes | 1/0 |     |
| default_language | Data | No  |     |     |
| settings_ref | Link(Chama Settings) | No  | convenience link |     |
| archived_on | Datetime | No  |     |     |
| created_by | Link(User) | Yes |     |     |
| created_on | Datetime | Yes |     |     |

**Status Enum**

Active  
Inactive  
Archived

**Constraints**

validate():  
enforce_unique(\["chama_name"\])  
enforce_unique(\["chama_code"\])

**B. DocType: Chama Context Session**

**Purpose**

Stores or logs user context switches where needed for traceability and mobile/web state sync.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Context Session ID | Data (Auto) | Yes |     |
| user | Link(User) | Yes |     |     |
| active_chama | Link(Chama) | Yes | selected tenant |     |
| switched_at | Datetime | Yes |     |     |
| switched_by | Link(User) | Yes | normally same as user |     |
| source_channel | Select | Yes | WEB / MOBILE / API |     |
| session_identifier | Data | No  | optional session token/correlation |     |
| previous_chama | Link(Chama) | No  | prior context |     |

This may be persisted as a log rather than a long-lived session record if performance/design prefers session storage plus audit logs.

**C. Global Requirement: chama field on tenant-owned records**

All tenant-owned DocTypes must contain:

| **Field Name** | **Type** | **Req** |
| --- | --- | --- |
| chama | Link(Chama) | Yes |

This applies to at least:

- Chama Member
- Loan extensions / guarantors / snapshots
- Contribution categories, cycles, obligations, payments, waivers
- Disbursement requests and executions
- Financial periods, reconciliations, issues, adjustments, statements
- Notifications and inbox
- Meetings, minutes, attendance, actions
- Proposals, votes, resolutions
- Budgets and amendments
- Investments and ownership/valuation/returns/distributions

**D. Optional DocType: Platform Tenant Admin Assignment**

**Purpose**

Defines which users may act as cross-tenant platform admins/support.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| user | Link(User) | Yes |
| admin_scope | Select | Yes |
| active | Check | Yes |
| notes | Small Text | No  |

**Admin Scopes**

- Full Platform Admin
- Tenant Provisioning Admin
- Read-Only Support
- Migration Admin

This must be rare and heavily audited.

**4.11.6 TENANT ISOLATION MODEL**

Tenant isolation must be enforced through several layers.

**A. Data Ownership Layer**

Every tenant-owned record has a mandatory chama.

**B. Query Filtering Layer**

Every query for tenant-owned records must include Chama scoping.

**Required filter pattern**

doc.chama == current_user_selected_chama

**For APIs**

If the endpoint is tenant-scoped, it must:

- infer current Chama from validated context
- or require explicit Chama and validate membership/access

**C. Permission Layer**

A user may only read/write tenant-owned records for Chamas where that user has a valid membership/role or platform-admin scope.

**D. UI Layer**

List views, dashboards, filters, and linked records must respect active Chama context.

**E. Export Layer**

Reports and exports must never mix records from multiple Chamas unless:

- caller is authorized cross-tenant admin
- export is explicitly platform-level
- audit log records the action

**4.11.7 USER-TO-CHAMA MEMBERSHIP MODEL**

A user may belong to multiple Chamas.

**A. Relationship**

User (1) ↔ (Many) Chama Member records  
Chama (1) ↔ (Many) Chama Member records

**B. Example**

| **User** | **Chama** | **Member ID** | **Role** |
| --- | --- | --- | --- |
| user@example.com | Umoja Chama | MB-0001 | Treasurer |
| user@example.com | Harvest Chama | MB-0204 | Member |

**C. Implication**

The same user:

- can be Treasurer in one Chama
- regular Member in another
- suspended in one
- active in another

All state and permissions must be tenant-specific.

**4.11.8 ACTIVE CHAMA CONTEXT ENGINE**

This is one of the most important operational mechanisms.

**A. Purpose**

The user must always act within an explicit Chama context.

**B. Context Sources**

- web session selection
- mobile app selection
- API header/body/query parameter plus authenticated validation

**C. Required Behavior**

When active Chama context changes:

- all lists refresh to new Chama
- dashboards refresh
- permissions resolve against that Chama
- notifications/inbox display for that Chama only unless unified inbox mode is intentionally provided
- create actions stamp new records with that Chama

**D. Context Switch Pseudocode**

def switch_user_chama_context(user, chama, source_channel):  
ensure_user_has_access_to_chama(user, chama)  
set_session_current_chama(user, chama)  
log_context_switch(user, chama, source_channel)

**E. Context Switch Constraints**

- user cannot switch to Chama without valid access
- archived Chama may be read-only if access allowed
- inactive Chama behavior depends on platform policy

**4.11.9 ROLE RESOLUTION BY CHAMA**

Roles are not global in practical business meaning.

**A. Rule**

When evaluating permissions for a user action:

1.  identify current Chama context
2.  resolve member record for that user in that Chama
3.  resolve active Chama role assignments
4.  resolve resulting permission set

**B. Example**

A global ERPNext role may grant access to a workspace, but the business action must still be checked against:

- active Chama membership
- role assignment in that Chama
- status in that Chama

**C. Pseudocode**

def get_effective_chama_roles(user, chama):  
member = get_member_for_user_in_chama(user, chama)  
if not member or member.status not in \["Active", "Dormant", "Suspended", "Exit In Progress"\]:  
return \[\]  
return get_active_roles_for_member(member)

**4.11.10 CHAMA SETTINGS PARTITIONING**

Each Chama shall have independent settings.

**A. Settings that must be Chama-scoped**

- contribution rules
- penalty rules
- loan rules/limits
- budget overrun mode
- notification defaults
- quorum rules
- voting rules
- exit policies
- investment liquidity policies

**B. Storage**

Use Chama Settings linked one-to-one or one-to-many structured settings records.

**C. Rule**

No Chama may accidentally inherit operational settings from another unless a template/provisioning flow explicitly clones defaults.

**4.11.11 ACTION DEFINITIONS**

**A. Create Chama**

**Input**

{  
"chama_name": "Umoja Chama",  
"chama_code": "UMOJA",  
"base_currency": "KES",  
"timezone": "Africa/Nairobi",  
"allow_new_member_applications": true  
}

**Process**

1.  validate uniqueness
2.  create Chama
3.  create default settings
4.  optionally assign owner/admin
5.  log provisioning

**Output**

{  
"status": "success",  
"data": {  
"chama_id": "CH-0001",  
"status": "Active"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MC001 | Chama name already exists |
| MC002 | Chama code already exists |
| MC003 | User not authorized to provision Chama |

**B. Switch Active Chama Context**

**Input**

{  
"chama": "CH-0001",  
"source_channel": "MOBILE"  
}

**Process**

- verify user access
- update current context
- log switch

**Output**

{  
"status": "success",  
"data": {  
"active_chama": "CH-0001"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MC101 | User does not have access to this Chama |
| MC102 | Chama is archived or unavailable |
| MC103 | Context switch failed |

**C. Get My Chamas**

**Input**

Authenticated user only

**Process**

- fetch all Chamas where user has valid membership or admin assignment
- return role summary and status per Chama

**Output**

{  
"status": "success",  
"data": {  
"chamas": \[  
{  
"chama": "CH-0001",  
"chama_name": "Umoja Chama",  
"member_id": "MB-0001",  
"roles": \["Treasurer"\],  
"member_status": "Active"  
},  
{  
"chama": "CH-0002",  
"chama_name": "Harvest Chama",  
"member_id": "MB-0204",  
"roles": \["Member"\],  
"member_status": "Active"  
}  
\]  
},  
"errors": \[\]  
}

**D. Archive Chama**

**Input**

{  
"chama": "CH-0001",  
"reason": "Group closed after final settlement"  
}

**Process**

1.  verify no blocking open processes or apply archive policy
2.  set Chama status Archived
3.  set all future-create actions blocked
4.  preserve readonly access as configured
5.  log archive

**Output**

{  
"status": "success",  
"data": {  
"chama": "CH-0001",  
"status": "Archived"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| MC201 | Chama has unresolved active processes |
| MC202 | User not authorized to archive |
| MC203 | Chama already archived |

**4.11.12 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Chama Selector (Mobile/Web)**

**Purpose**

Allow user to choose active tenant context.

**Fields**

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| chama_name | Data | display name |
| chama_code | Data | short code |
| role_summary | Data | e.g. Treasurer |
| member_status | Badge | Active/Suspended/etc |
| active_indicator | Check/icon | currently selected |

**Actions**

- Switch to Chama
- View Chama summary

**Rules**

- only Chamas the user can access are shown
- archived Chamas may appear separately and as readonly if policy allows
- switching must be explicit, not inferred from last action only

**B. Screen: Chama Management (Admin)**

**Sections**

1.  Tenant identity
2.  Tenant settings summary
3.  Member count / status summary
4.  Provisioning metadata
5.  Archive/inactivate actions

**Actions**

- Create Chama
- Edit Chama metadata
- Activate / Inactivate
- Archive
- View tenant diagnostics

**C. Screen: Multi-Chama User View**

**Purpose**

Support users with more than one Chama.

**Display**

- all accessible Chamas
- role in each
- member status in each
- recent activity per Chama (optional)
- quick switch

**D. Screen: Tenant Diagnostics (Admin/Support)**

**Display**

- total records by module for selected Chama
- active users count
- pending approvals
- last context-switch error or integrity issues
- notifications backlog
- tenant configuration completeness

This is admin/support only.

**4.11.13 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** | **Platform Admin** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| View own accessible Chamas | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Switch context | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Create Chama | No  | No  | No  | No  | No  | Limited/No by business policy | Yes |
| Edit Chama metadata | No  | No  | No  | No  | No  | Limited | Yes |
| Archive Chama | No  | No  | No  | No  | No  | No/Limited | Yes |
| View tenant diagnostics | No  | No  | No  | No  | No  | Limited | Yes |
| View cross-tenant data | No  | No  | No  | No  | No  | No unless explicit | Yes (scoped and audited) |

**B. Field-Level Examples**

| **DocType** | **Field** | **Member** | **Admin** | **Platform Admin** |
| --- | --- | --- | --- | --- |
| Chama | status | Read own-access Chama | Limited | Write |
| Chama | owner_user | No  | Read | Write |
| Context Session | active_chama | Read own | Read own if admin user | Read |
| Platform Tenant Admin Assignment | admin_scope | No  | No  | Write |

**C. Critical Restriction**

Having a global ERPNext administrative role must not automatically imply unrestricted business access to all Chama records unless the user is explicitly acting under platform-admin scope and such access is logged.

**4.11.14 NOTIFICATION MATRIX**

| **Event** | **Trigger** | **Recipient** | **Channel** | **Template Key** | **Priority** |
| --- | --- | --- | --- | --- | --- |
| chama_created | provisioning complete | owner/admin | APP/EMAIL optional | chama_created | Medium |
| chama_archived | archive | relevant officials / members summary | APP | chama_archived | High |
| context_switch_failed | invalid switch attempt | user / admin if suspicious | APP | context_switch_failed | Medium |
| suspicious_cross_tenant_access | security rule hit | platform admin/security | APP/SMS | suspicious_cross_tenant_access | Critical |
| tenant_configuration_incomplete | diagnostics rule hit | admin/platform admin | APP | tenant_configuration_incomplete | Medium |

**Example Template: chama_archived**

The Chama "{chama_name}" has been archived. Historical records remain available according to platform policy.

**4.11.15 API ENDPOINTS (FULL)**

**A. Get My Chamas**

GET /api/method/chama.platform.my_chamas

**B. Switch Context**

POST /api/method/chama.platform.switch_context

**C. Create Chama**

POST /api/method/chama.platform.create_chama

**D. Get Chama Detail**

GET /api/method/chama.platform.chama_detail?chama=CH-0001

**E. Archive Chama**

POST /api/method/chama.platform.archive_chama

**F. Tenant Diagnostics**

GET /api/method/chama.platform.tenant_diagnostics?chama=CH-0001

**Example Response**

{  
"status": "success",  
"data": {  
"active_chama": "CH-0001",  
"chama_name": "Umoja Chama",  
"roles": \["Treasurer"\],  
"member_status": "Active"  
},  
"errors": \[\]  
}

**4.11.16 REPORTS**

**A. Chama Register**

**Columns**

- Chama ID
- Chama Name
- Code
- Status
- Created On
- Base Currency
- Owner User

**B. User Multi-Chama Access Report**

**Columns**

- User
- Chama
- Member ID
- Roles
- Member Status

**C. Tenant Diagnostics Report**

**Columns**

- Chama
- Active Members
- Pending Proposals
- Open Reconciliation Issues
- Notification Failures
- Last Activity Date

**D. Cross-Tenant Access Audit Report**

**Purpose**

Support auditing of platform-admin or support actions.

**Columns**

- User
- Access Scope
- Chama
- Action
- Timestamp
- Reason / Ticket Reference

**4.11.17 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama | Required |
| Custom DocType | Chama Context Session | Recommended/logging |
| Global Field Rule | chama on tenant-owned records | Mandatory |
| Optional DocType | Platform Tenant Admin Assignment | Recommended |
| Reports | tenant register / multi-chama access / diagnostics / access audit | Required |
| API | context switching and tenant retrieval | Required |
| Integration | all modules must enforce Chama scope | Mandatory |

**4.11.18 WORKFLOW CONFIGURATION**

**Workflow Name: Chama Lifecycle**

| **State** | **Meaning** |
| --- | --- |
| Active | fully operational |
| Inactive | temporarily unavailable for new operations |
| Archived | closed / historical readonly |

No complex workflow is required unless platform governance wants formal archive approval.

**4.11.19 SERVER LOGIC / HOOKS**

**A. Universal Tenant Validation Hook**

This is a cross-module requirement.

def validate_doc_chama_access(doc, user):  
active_chama = get_current_session_chama(user)  
if hasattr(doc, "chama") and doc.chama != active_chama:  
frappe.throw("Record does not belong to active Chama context")

**B. Query Filter Helper**

def apply_chama_filter(filters, user):  
active_chama = get_current_session_chama(user)  
filters\["chama"\] = active_chama  
return filters

**C. Context Switch**

def switch_context(user, chama, source_channel):  
ensure_user_has_access_to_chama(user, chama)  
set_current_session_chama(user, chama)  
log_context_switch(user, chama, source_channel)

**D. Tenant Archive Check**

def archive_chama(chama):  
ensure_no_blocking_active_processes(chama)  
chama_doc = frappe.get_doc("Chama", chama)  
chama_doc.status = "Archived"  
chama_doc.archived_on = now()  
chama_doc.save()

**4.11.20 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| User belongs to multiple Chamas and opens stale deep link | link Chama mismatch vs current context | prompt switch or deny access | Yes |
| Same phone/email across Chamas | duplicate across tenants | allow if user/member mapping valid | Yes |
| Archived Chama still has active members | archive validation | allow readonly archive or block until closure policy met | Yes |
| Record created without Chama due to bug/import | missing mandatory field | block save/import, raise integrity issue | Yes |
| API called with explicit Chama different from session context | mismatch | reject unless privileged platform admin flow | Yes |
| Cross-tenant report accidentally mixes data | report validation | block execution and log | Yes |
| Platform admin support access | elevated support action | require reason/ticket and log | Yes |

**4.11.21 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| All modules | every business record depends on tenant scoping |
| Member Lifecycle | same user may hold multiple tenant memberships |
| Notifications | communication must remain Chama-specific |
| Analytics | dashboards and reports must never leak cross-tenant data by default |
| Security/Audit | cross-tenant actions require special logging and controls |

**4.11.22 CRITICAL IMPLEMENTATION RULES**

- Every tenant-owned business record must include chama
- Tenant isolation must be enforced at model, query, permission, API, and report levels
- Context switching must be explicit and logged
- A user’s role must always be resolved relative to the active Chama
- Cross-tenant access must be exceptional, authorized, and auditable
- Archived Chamas must remain historically intact; no archive operation may imply data deletion
- Platform administration must not bypass business audit requirements
- Exports must not mix tenant data unless explicitly authorized and logged

## MODULE 4.12 — ANALYTICS & REPORTING

**4.12.1 MODULE OWNERSHIP**

| **Layer** | **Owner** |
| --- | --- |
| Source transactional data | All business modules |
| Metric definitions and calculations | Custom |
| Dashboards and KPI cards | Custom + Frappe/ERPNext UI |
| Reports and drill-down queries | ERPNext reports + custom script/query reports |
| Export generation | ERPNext/Frappe + custom formatting |
| Tenant/report security | ERPNext/Frappe + custom enforcement |
| Statement and snapshot consumption | Reconciliation / Member Lifecycle / Investment / Budgeting |

**4.12.2 MODULE PURPOSE**

The Analytics & Reporting module shall manage:

- real-time and periodic dashboards
- operational and management reports
- cross-module KPI computation
- trend analysis
- drill-down from summary to source records
- member-facing statements and summaries
- officer-facing financial and governance insights
- report exports
- report scheduling (future-ready)
- tenant-safe reporting access

This module must explicitly separate:

1.  **Metric**  
    a calculated indicator such as repayment rate or contribution compliance
2.  **Dashboard**  
    a visual grouping of metrics and charts
3.  **Report**  
    a tabular or structured output, optionally exportable
4.  **Snapshot**  
    a time-bound stored reporting result or statement output
5.  **Drill-Down Path**  
    the route from a summary figure to underlying records

That separation is mandatory.

**4.12.3 ERPNext IMPLEMENTATION STRATEGY**

This module shall use a hybrid approach.

**Reuse from ERPNext / Frappe**

- report builder concepts where appropriate
- query reports
- script reports
- workspaces
- charts
- dashboard cards
- list/report permissions
- export capabilities
- scheduled jobs for pre-computation if needed

**Custom Chama layer**

- Chama-specific metric formulas
- dashboard assemblies
- cross-module drill-down logic
- member summary views
- risk scoring / risk panels
- cached KPI tables if performance requires
- report security wrappers tied to active Chama context

**Rule**

No dashboard or report may invent its own logic independently if the same metric is already defined elsewhere.  
Metric definitions must be centralized and reused.

**4.12.4 REPORTING DOMAINS**

The reporting layer shall cover at least these domains:

| **Domain** | **Coverage** |
| --- | --- |
| Financial Overview | inflows, outflows, balances, net position |
| Contributions | expected vs paid, overdue, compliance |
| Loans | issued, active, overdue, default, repayment |
| Disbursements | request, approval, execution, by type |
| Reconciliation | expected vs actual, variance, issues |
| Governance | meetings, attendance, quorum, voting participation |
| Budgeting | allocated vs actual, overruns, amendments |
| Member Lifecycle | active/inactive/dormant/exited, tenure, churn |
| Investment | valuation, returns, ownership, entitlement |
| Platform/Tenant | per-Chama diagnostics and usage (authorized only) |

**4.12.5 DATA MODEL (FULL)**

This module mostly reads from other modules, but it still requires some dedicated metadata/configuration structures.

**A. DocType: Chama Report Definition**

**Purpose**

Represents a registered report artifact available in the platform.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Report Definition ID | Data (Auto) | Yes |     |
| chama | Chama | Link(Chama) | No  | null allowed for global shared report definitions |
| report_code | Data | Yes | unique identifier |     |
| report_name | Data | Yes | human-readable name |     |
| report_domain | Select | Yes | Financial / Contributions / Loans / Governance / etc |     |
| report_type | Select | Yes | Dashboard / Query Report / Script Report / Statement / Export |     |
| audience_type | Select | Yes | Member / Treasurer / Chair / Auditor / Admin / Platform Admin |     |
| source_modules | Data / JSON | No  | related modules |     |
| active | Check | Yes | 1   |     |
| supports_export_pdf | Check | Yes | 0/1 |     |
| supports_export_xlsx | Check | Yes | 0/1 |     |
| supports_drilldown | Check | Yes | 0/1 |     |
| config_json | JSON / Long Text | No  | visualization/filter config |     |

**Constraint**

Global reports must not expose tenant-mixed data to normal users.

**B. DocType: Chama Metric Definition**

**Purpose**

Central catalog of metric formulas and display metadata.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** | **Description** |
| --- | --- | --- | --- | --- |
| name | Metric ID | Data (Auto) | Yes |     |
| metric_code | Data | Yes | unique key, e.g. loan_default_rate |     |
| metric_name | Data | Yes |     |     |
| metric_domain | Select | Yes | Financial / Loans / Contributions / etc |     |
| description | Small Text | Yes |     |     |
| formula_text | Long Text | Yes | human-readable formula |     |
| computation_type | Select | Yes | Real-Time / Cached / Snapshot |     |
| decimal_places | Int | Yes | default display precision |     |
| unit_type | Select | Yes | Currency / Percent / Count / Ratio / Number |     |
| source_dependencies | JSON / Long Text | No  | modules/doctypes used |     |
| active | Check | Yes | 1   |     |
| owner_module | Data | Yes | authoritative owner |     |
| drilldown_route | Data | No  | route template if applicable |     |

**Rule**

Each metric code must be unique platform-wide.

**C. DocType: Chama Metric Snapshot**

**Purpose**

Stores optionally cached metric values for performance and historical reporting.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Snapshot ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| metric_code | Data | Yes |     |
| snapshot_date | Datetime | Yes |     |
| value_number | Float | No  |     |
| value_currency | Currency | No  |     |
| value_text | Data | No  |     |
| period_ref | Link(Chama Financial Period) | No  |     |
| computed_by | Link(User) | No  |     |
| computation_run_ref | Data | No  |     |
| source_hash | Data | No  |     |

**Rule**

Use only for metrics designated Cached or Snapshot.

**D. DocType: Chama Dashboard Layout**

**Purpose**

Stores a configured dashboard definition.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Dashboard ID | Data (Auto) | Yes |
| chama | Link(Chama) | No  | null allowed for global template |
| dashboard_code | Data | Yes |     |
| dashboard_name | Data | Yes |     |
| audience_type | Select | Yes |     |
| active | Check | Yes |     |
| layout_json | Long Text / JSON | Yes |     |
| default_filters_json | Long Text / JSON | No  |     |

**Purpose of layout_json**

Defines:

- cards
- charts
- order
- metric bindings
- drill-down routes

**E. DocType: Chama Saved Report Request**

**Purpose**

Stores user-generated saved report filters / reusable report configurations.

**Fields**

| **Field Name** | **Label** | **Type** | **Req** |
| --- | --- | --- | --- |
| name | Saved Report ID | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |     |
| user | Link(User) | Yes |     |
| report_definition | Link(Chama Report Definition) | Yes |     |
| saved_name | Data | Yes |     |
| filter_json | Long Text / JSON | Yes |     |
| visibility | Select | Yes |     |

**Visibility**

- Private
- Shared within Chama Role
- Shared within Chama Admins

**F. Optional DocType: Chama Report Export Log**

**Purpose**

Audit export activity, especially for sensitive reports.

**Fields**

| **Field** | **Type** | **Req** |
| --- | --- | --- |
| name | Data (Auto) | Yes |
| chama | Link(Chama) | Yes |
| report_definition | Link(Chama Report Definition) | Yes |
| exported_by | Link(User) | Yes |
| exported_at | Datetime | Yes |
| export_format | Select | Yes |
| filter_json | Long Text | No  |
| file_ref | Attach | No  |

**4.12.6 METRIC CATALOGUE (IMPLEMENTATION DEFINITIONS)**

Below are the baseline core metrics. These definitions must be canonical.

**A. Financial Metrics**

**1\. total_inflow**

total_inflow =  
contribution_payments  
\+ loan_repayments  
\+ investment_returns_realized  
\+ other_approved_inflows

**2\. total_outflow**

total_outflow =  
executed_disbursements  
\+ loan_disbursements  
\+ investment_outflows  
\+ other_approved_outflows

**3\. net_balance**

net_balance = total_inflow - total_outflow + opening_balance + posted_adjustments_net

**4\. liquidity_ratio**

A configurable ratio; recommended default:

liquidity_ratio = liquid_funds / short_term_obligations

**B. Contribution Metrics**

**1\. contribution_expected_total**

sum(amount_due for open/period obligations)

**2\. contribution_paid_total**

sum(valid allocated payments within period)

**3\. contribution_overdue_total**

sum(amount_outstanding for overdue obligations)

**4\. contribution_compliance_rate**

contribution_compliance_rate = contribution_paid_total / contribution_expected_total

**5\. contribution_collection_rate**

Can be the same as compliance or defined by period cash collection:

collection_rate = collected_in_period / due_in_period

**C. Loan Metrics**

**1\. loans_total_issued**

sum(approved/disbursed loan principal in period)

**2\. loans_active_balance**

sum(outstanding principal or total active balances)

**3\. loans_overdue_total**

sum(outstanding balances of overdue loans)

**4\. loan_default_rate**

loan_default_rate = defaulted_loan_count / total_active_or_issued_loan_count

**5\. repayment_rate**

repayment_rate = amount_repaid / amount_due_for_repayment

**6\. average_loan_size**

average_loan_size = total_issued_amount / number_of_issued_loans

**D. Disbursement Metrics**

**1\. total_disbursements_by_type**

Grouped sum of executed disbursements by request type.

**2\. disbursement_approval_turnaround**

approval_turnaround = approval_timestamp - request_date

**3\. disbursement_execution_turnaround**

execution_turnaround = execution_date - approval_timestamp

**E. Reconciliation Metrics**

**1\. reconciliation_variance_total**

actual_total_balance - expected_total_balance

**2\. open_reconciliation_issue_count**

Count of reconciliation issues in Open/Investigating.

**3\. average_issue_resolution_time**

avg(resolved_on - opened_on)

**F. Governance Metrics**

**1\. meeting_attendance_rate**

attendance_rate = present_count / eligible_attendee_count

**2\. quorum_achievement_rate**

quorum_achievement_rate = meetings_with_quorum / total_meetings

**3\. voting_participation_rate**

voting_participation_rate = actual_vote_count / eligible_voter_count

**4\. resolution_enforcement_success_rate**

applied_resolutions / approved_resolutions

**G. Budget Metrics**

**1\. budget_total_allocated**

**2\. budget_total_actual**

**3\. budget_variance**

budget_variance = total_actual - total_allocated

**4\. budget_compliance_rate**

non_overrun_lines / total_active_budget_lines

**H. Member Lifecycle Metrics**

**1\. active_member_count**

**2\. dormant_member_count**

**3\. suspended_member_count**

**4\. membership_churn_rate**

Recommended default:

churn_rate = exited_members_in_period / active_members_at_period_start

**5\. average_member_tenure**

avg(today - join_date for relevant members)

**I. Investment Metrics**

**1\. total_investment_cost**

**2\. current_portfolio_value**

**3\. unrealized_gain_loss_total**

**4\. realized_return_total**

**5\. roi**

Recommended:

roi = realized_return_total / total_investment_cost

or configurable to include unrealized changes.

**4.12.7 DASHBOARD DEFINITIONS**

Dashboards must be audience-specific.

**A. Dashboard: Member Dashboard**

**Audience**

Member

**KPIs**

- My Contributions Due
- My Overdue Contributions
- My Active Loans
- My Next Loan Repayment Due
- My Investment Entitlement
- My Notifications Count

**Charts / Panels**

- Contribution history trend
- Loan repayment schedule snapshot
- Investment entitlement summary

**Drill-Down Targets**

- contribution statement
- loan detail
- investment detail
- member statement

**B. Dashboard: Treasurer Dashboard**

**Audience**

Treasurer

**KPIs**

- Total Contributions Collected This Period
- Total Overdue Contributions
- Active Loan Portfolio
- Overdue Loans
- Total Executed Disbursements
- Current Reconciliation Variance
- Open Reconciliation Issues
- Budget Overrun Count

**Charts**

- contribution collection trend
- loan portfolio aging
- disbursement by type
- budget vs actual
- reconciliation variance trend

**Alerts Panel**

- failed notifications
- pending disbursement approvals
- overdue action items
- large variance alerts

**C. Dashboard: Chair Dashboard**

**Audience**

Chair

**KPIs**

- Open Proposals
- Pending Approvals
- Quorum Achievement Rate
- Default Rate
- High-Risk Alerts
- Active Investment Value
- Budget Overrun Escalations

**Charts**

- governance participation trend
- default and overdue trend
- investment valuation trend

**D. Dashboard: Auditor Dashboard**

**Audience**

Auditor / Oversight

**KPIs**

- Reconciliation issues open
- Adjustment entries this period
- Reversed payments/disbursements
- Closed periods count
- Resolution enforcement failures

**Charts / Panels**

- audit exception register
- correction trend analysis
- export activity summary

**E. Dashboard: Platform Admin Dashboard**

**Audience**

Platform Admin only

**KPIs**

- Active Chamas
- Total Users
- Total Active Members Across Platform
- Queue Failures
- Tenant Diagnostics Alerts

**Rule**

This dashboard must never expose tenant business details beyond authorized platform scope.

**4.12.8 REPORT DEFINITIONS (IMPLEMENTATION LEVEL)**

**A. Report: Member Statement**

**Purpose**

Provide a member-specific consolidated view for a selected period.

**Filters**

- Chama (implicit from context)
- Member
- From Date
- To Date
- Financial Period (optional)

**Sections / Columns**

1.  profile summary
2.  contribution due/paid/overdue
3.  loans and repayments
4.  disbursements received
5.  investment entitlement and returns
6.  settlement/exit status if applicable
7.  closing member position

**Security**

Members can view only own statement.  
Officials can view member statements according to role.

**B. Report: Financial Overview Report**

**Filters**

- Chama
- Period / date range

**Output**

- opening balance
- total inflow
- total outflow
- posted adjustments
- closing expected balance
- latest actual balance / variance

**C. Report: Contribution Compliance Report**

**Filters**

- Chama
- Date range
- Category
- Member status
- Member

**Columns**

- Member
- Category
- Amount Due
- Amount Paid
- Outstanding
- Status
- Compliance %

**D. Report: Loan Portfolio Report**

**Filters**

- Chama
- Loan product
- Status
- Date range
- Member

**Columns**

- Loan ID
- Borrower
- Principal
- Outstanding
- Status
- Days Overdue
- Guarantor Count
- Next Due Date

**E. Report: Disbursement Register**

**Filters**

- Chama
- Type
- Status
- Beneficiary
- Date range

**Columns**

- Request ID
- Execution ID
- Type
- Beneficiary
- Approved Amount
- Executed Amount
- Execution Status

**F. Report: Reconciliation Summary**

**Filters**

- Chama
- Financial Period
- Source Type
- Status

**Columns**

- Reconciliation ID
- Date
- Expected Balance
- Actual Balance
- Variance
- Status
- Issue Count

**G. Report: Governance Participation Report**

**Filters**

- Chama
- Date range
- Meeting type
- Proposal type

**Columns**

- Meeting
- Attendance %
- Quorum Achieved
- Proposal
- Eligible Voters
- Actual Votes
- Participation %

**H. Report: Budget vs Actual**

**Filters**

- Chama
- Budget
- Budget Type
- Date range

**Columns**

- Budget
- Line Item
- Allocated
- Actual
- Remaining
- Utilization %
- Overrun Flag

**I. Report: Investment Portfolio Report**

**Filters**

- Chama
- Investment type
- Status

**Columns**

- Investment
- Acquisition Cost
- Current Valuation
- Unrealized Gain/Loss
- Realized Returns
- Owners Count

**J. Report: Member Lifecycle Report**

**Filters**

- Chama
- Status
- Role
- Join date range
- Exit date range

**Columns**

- Member
- Join Date
- Status
- Role
- Tenure
- Exit Date
- Final Settlement

**4.12.9 DRILL-DOWN MODEL**

Drill-down behavior must be explicit and consistent.

**A. Rule**

Every summary metric shown on a dashboard must map to:

- a report
- or a filtered list
- or a detail page

**B. Examples**

| **Summary Metric** | **Drill-Down Target** |
| --- | --- |
| Overdue Contributions | Overdue Contributions Report |
| Active Loans | Loan Portfolio filtered status=Active |
| Open Reconciliation Issues | Reconciliation Issue list filtered open |
| Budget Overrun Count | Budget vs Actual filtered overrun=true |
| Voting Participation Rate | Governance Participation Report |

**C. Security**

Drill-down must preserve:

- active Chama context
- role-based access
- allowed columns only

**4.12.10 EXPORT MODEL**

Reports must support controlled export.

**A. Export Formats**

- PDF
- XLSX/CSV
- JSON (API responses; limited use)

**B. Export Rules**

- exported data must match filtered on-screen data
- export action must be permission-gated
- sensitive reports should log export activity
- member-facing exports should be limited to own data

**C. Export Log**

For sensitive reports or high-privilege exports:

- user
- Chama
- report
- filters
- export format
- timestamp

must be logged.

**4.12.11 ACTION DEFINITIONS**

**A. Load Dashboard**

**Input**

{  
"dashboard_code": "TREASURER_MAIN",  
"chama": "CH-0001",  
"period": "FP-2026-04"  
}

**Process**

1.  validate dashboard access
2.  resolve metric definitions
3.  compute or fetch cached values
4.  load charts/cards
5.  return drill-down routes

**Output**

{  
"status": "success",  
"data": {  
"dashboard_name": "Treasurer Dashboard",  
"cards": \[  
{  
"metric_code": "contribution_paid_total",  
"label": "Collected This Period",  
"value_currency": 250000  
}  
\],  
"charts": \[\]  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| AN001 | Dashboard not found |
| AN002 | User not authorized for dashboard |
| AN003 | Metric computation failed |

**B. Generate Report**

**Input**

{  
"report_code": "LOAN_PORTFOLIO",  
"chama": "CH-0001",  
"filters": {  
"status": "Active",  
"from_date": "2026-04-01",  
"to_date": "2026-04-30"  
}  
}

**Process**

- validate access
- validate filters
- execute report logic
- return rows + metadata

**Output**

{  
"status": "success",  
"data": {  
"report_name": "Loan Portfolio Report",  
"columns": \["Loan ID", "Borrower", "Outstanding", "Status"\],  
"rows": \[  
\["LN-0001", "Jane Doe", 15000, "Active"\]  
\],  
"row_count": 1  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| AN101 | Invalid report filters |
| AN102 | Report not available to this role |
| AN103 | Report execution timeout or failure |

**C. Export Report**

**Input**

{  
"report_code": "BUDGET_VS_ACTUAL",  
"chama": "CH-0001",  
"filters": {  
"budget": "BGT-0004"  
},  
"format": "XLSX"  
}

**Process**

- validate export permission
- generate report dataset
- render export file
- optionally log export

**Output**

{  
"status": "success",  
"data": {  
"file_name": "budget_vs_actual_BGT-0004.xlsx"  
},  
"errors": \[\]  
}

**Errors**

| **Code** | **Message** |
| --- | --- |
| AN201 | Export not permitted for this report |
| AN202 | Unsupported export format |
| AN203 | Export generation failed |

**D. Save Report Filter Set**

**Input**

{  
"report_definition": "RPT-0004",  
"saved_name": "My Monthly Active Loans",  
"filter_json": {  
"status": "Active",  
"period": "FP-2026-04"  
},  
"visibility": "Private"  
}

**Output**

{  
"status": "success",  
"data": {  
"saved_report_id": "SRR-0001"  
},  
"errors": \[\]  
}

**4.12.12 SCREEN SPECIFICATIONS (FIELD-LEVEL)**

**A. Screen: Dashboard Home (Role-Specific)**

**Components**

- KPI cards
- charts
- risk alerts
- pending items
- drill-down quick links

**Common Fields per Card**

| **Field** | **Type** |
| --- | --- |
| metric_name | Data |
| metric_value | Currency/Float/Int |
| metric_change_indicator | Float / arrow |
| last_updated | Datetime |
| drilldown_route | Data |

**Rules**

- cards ordered by dashboard layout
- stale cached metrics should show timestamp
- empty charts must show “No data” instead of breaking

**B. Screen: Reports Explorer**

**Fields**

- report list
- search bar
- domain filter
- favorites
- saved report views

**Actions**

- Open Report
- Save Filters
- Export
- Pin to Favorites

**C. Screen: Report Viewer**

**Sections**

1.  Filters panel
2.  Summary metrics strip (optional)
3.  Table output
4.  Export controls
5.  Drill-down links

**Grid Behavior**

- pagination for large datasets
- sortable columns where possible
- sticky filter context shown on top

**D. Screen: Member Statement View (Mobile/Web)**

**Sections**

- profile header
- financial summary
- contributions
- loans
- disbursements
- investments
- closing position

**Actions**

- change period
- export PDF
- drill into underlying sections

**4.12.13 PERMISSIONS (FIELD + ACTION LEVEL)**

**A. Role Matrix**

| **Action** | **Member** | **Treasurer** | **Chair** | **Secretary** | **Auditor** | **Admin** | **Platform Admin** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| View own dashboard | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| View member statement (own) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| View all financial dashboards in Chama | No  | Yes | Yes | No  | Yes | Yes | No unless support scope |
| View governance dashboards | No  | Limited | Yes | Yes | Yes | Yes | No unless support scope |
| Generate financial reports | No/self only | Yes | Yes | Limited | Yes | Yes | Limited |
| Export sensitive reports | No/self only | Limited | Limited | No  | Yes | Yes | Yes audited |
| View platform-wide analytics | No  | No  | No  | No  | No  | No  | Yes |

**B. Field-Level Examples**

| **Report / View** | **Field** | **Member** | **Treasurer** | **Auditor** | **Platform Admin** |
| --- | --- | --- | --- | --- | --- |
| Member Statement | other members’ rows | No  | Read | Read | Scoped support only |
| Loan Portfolio | guarantor details | No  | Read | Read | Scoped support only |
| Tenant Diagnostics | cross-tenant counts | No  | No  | No  | Read |
| Export Log | exported_by | No  | Limited | Read | Read |

**C. Rule**

No member-level user may access another member’s detailed personal financial report unless their Chama role explicitly allows it.

**4.12.14 CACHE / SNAPSHOT STRATEGY**

Not all metrics should be computed live.

**A. Real-Time Metrics**

Use live queries when:

- scope is narrow
- row counts are manageable
- freshness is critical

Examples:

- unread notifications
- my active loans
- my due contributions

**B. Cached Metrics**

Use scheduled snapshots when:

- computation is heavy
- dashboard cards are reused often
- same metric is viewed by many users

Examples:

- total portfolio value
- default rate
- budget compliance rate
- quorum achievement trend

**C. Snapshot Frequencies**

| **Metric Type** | **Frequency** |
| --- | --- |
| Operational KPI | hourly or near real-time |
| Financial summary | daily |
| Governance participation | daily |
| Monthly statement snapshots | on period close |

**D. Staleness Rule**

Cached metrics must display “last updated at” metadata.

**4.12.15 NOTIFICATION INTEGRATION**

This module may generate alerts from metric thresholds.

**A. Threshold-Based Alerts**

Examples:

- default rate exceeds threshold
- reconciliation variance exceeds threshold
- budget overrun count above threshold
- notification queue failures spike
- quorum achievement rate drops below threshold

**B. Alert Flow**

1.  threshold condition detected
2.  create analytics alert event
3.  send to configured audience

**C. Example Alert Template**

Risk alert: loan default rate has reached {metric_value}% in {chama_name}.

**4.12.16 API ENDPOINTS (FULL)**

**A. Load Dashboard**

GET /api/method/chama.analytics.dashboard?dashboard_code=TREASURER_MAIN&chama=CH-0001

**B. Get Metric**

GET /api/method/chama.analytics.metric?metric_code=loan_default_rate&chama=CH-0001

**C. Generate Report**

POST /api/method/chama.analytics.generate_report

**D. Export Report**

POST /api/method/chama.analytics.export_report

**E. Get Member Statement**

GET /api/method/chama.analytics.member_statement?member=MB-0001&period=FP-2026-04

**F. Save Report Filters**

POST /api/method/chama.analytics.save_report_request

**G. Load Saved Report**

GET /api/method/chama.analytics.saved_report?saved_report_id=SRR-0001

**Example Response**

{  
"status": "success",  
"data": {  
"metric_code": "contribution_compliance_rate",  
"value_number": 0.82,  
"unit_type": "Percent",  
"last_updated": "2026-05-01T08:00:00"  
},  
"errors": \[\]  
}

**4.12.17 REPORTS CATALOGUE (MANDATORY BASE SET)**

The platform shall ship with at least the following report definitions:

1.  Member Statement
2.  Financial Overview Report
3.  Contribution Compliance Report
4.  Loan Portfolio Report
5.  Overdue Loans Report
6.  Disbursement Register
7.  Reconciliation Summary
8.  Open Reconciliation Issues
9.  Budget vs Actual Report
10. Budget Overrun Report
11. Meeting Register
12. Attendance Report
13. Proposal Register
14. Governance Participation Report
15. Member Register
16. Membership Status Report
17. Exit & Settlement Register
18. Investment Register
19. Ownership Allocation Report
20. Investment Returns Report

This list is the minimum baseline.

**4.12.18 ERPNext CONFIGURATION SUMMARY**

| **Type** | **Item** | **Notes** |
| --- | --- | --- |
| Custom DocType | Chama Report Definition | Required |
| Custom DocType | Chama Metric Definition | Required |
| Custom DocType | Chama Metric Snapshot | Recommended |
| Custom DocType | Chama Dashboard Layout | Recommended |
| Custom DocType | Chama Saved Report Request | Recommended |
| Optional DocType | Chama Report Export Log | Recommended |
| Dashboards | member / treasurer / chair / auditor / platform | Required |
| Reports | baseline catalogue above | Required |
| Scheduler | metric cache jobs / threshold alert jobs | Recommended |
| Export support | PDF / XLSX | Required |

**4.12.19 SERVER LOGIC / HOOKS**

**A. Compute Metric**

def compute_metric(metric_code, chama, filters=None):  
definition = get_metric_definition(metric_code)  
if definition.computation_type == "Cached":  
return get_latest_metric_snapshot(metric_code, chama, filters)  
return compute_metric_live(metric_code, chama, filters)

**B. Build Dashboard**

def build_dashboard(dashboard_code, chama, user):  
layout = get_dashboard_layout(dashboard_code, chama, user)  
cards = \[\]  
for card in layout\["cards"\]:  
metric = compute_metric(card\["metric_code"\], chama, layout.get("default_filters"))  
cards.append({"metric_code": card\["metric_code"\], "value": metric})  
return {"cards": cards, "charts": build_charts(layout, chama)}

**C. Generate Report**

def generate_report(report_code, chama, filters, user):  
ensure_report_access(report_code, user, chama)  
validate_filters(report_code, filters)  
rows = run_report_query(report_code, chama, filters)  
return rows

**D. Snapshot Job**

def refresh_metric_snapshots():  
for chama in get_active_chamas():  
for metric in get_cached_metric_definitions():  
value = compute_metric_live(metric.metric_code, chama)  
store_metric_snapshot(chama, metric.metric_code, value)

**4.12.20 EDGE CASE HANDLING (EXPLICIT)**

| **Edge Case** | **Detection** | **Behavior** | **Audit Requirement** |
| --- | --- | --- | --- |
| Large dataset report | row count / timeout risk | paginate or require export async | Yes for sensitive reports |
| Cached metric stale | snapshot too old | show stale timestamp and optionally recompute | No special audit required |
| Missing source data | null/empty source results | show 0 or “No data” according to metric definition | Yes if materially impacts statement |
| Metric mismatch across screens | same metric code differs | block deployment / raise integrity issue | Yes |
| Cross-tenant report request | filters or code imply multiple tenants | reject unless authorized platform scope | Yes |
| Deleted/archived source record referenced in report | source inconsistency | preserve historical row values or flag | Yes |
| Export after permissions changed | permission re-check at export | block if no longer allowed | Yes |

**4.12.21 CROSS-MODULE DEPENDENCIES**

| **Upstream / Downstream** | **Dependency** |
| --- | --- |
| Contributions | contribution metrics and statements |
| Loans | portfolio, default, repayment metrics |
| Disbursements | outflow and turnaround metrics |
| Reconciliation | balance, variance, statement snapshots |
| Notifications | operational alert and engagement metrics |
| Meetings | attendance and quorum metrics |
| Voting | participation and enforcement metrics |
| Budgeting | allocated vs actual metrics |
| Member Lifecycle | status, churn, tenure metrics |
| Investments | valuation, entitlement, ROI metrics |
| Multi-Chama | tenant-safe reporting partitioning |

**4.12.22 CRITICAL IMPLEMENTATION RULES**

- Every report and dashboard must be Chama-scoped unless explicitly platform-level and authorized
- Metric definitions must be centralized and reused; duplicate formulas are not allowed
- Displayed KPI values must be traceable to source records or snapshots
- Exported reports must match visible filtered report output
- Cached metrics must display freshness metadata
- Member-facing views must never expose unauthorized cross-member data
- Drill-down must preserve context, filters, and security constraints
- Sensitive report exports should be logged
- Statement outputs must remain consistent with reconciliation and settlement logic

## SECTION 5: CROSS-MODULE RULES & CANONICAL FORMULAS

**5.1 PURPOSE OF THIS SECTION**

This section defines:

- shared formulas that all modules must use
- canonical rule precedence
- cross-module state dependencies
- common financial interpretations
- conflict resolution rules when multiple modules affect the same business object
- platform-wide behavioral invariants

These rules are mandatory for:

- UI logic
- API responses
- background jobs
- reports
- exports
- statements
- audits

No module may redefine these formulas independently.

**5.2 CANONICAL RULE HIERARCHY**

When rules conflict, the system shall resolve them in this order:

| **Priority** | **Rule Source** | **Description** |
| --- | --- | --- |
| 1   | Platform Safety Rules | non-negotiable technical/security/audit rules |
| 2   | Chama Constitutional / Governance Rules | voting, approval, quorum, role authority |
| 3   | Financial Integrity Rules | no-delete, reconciliation, settlement correctness |
| 4   | Module-Specific Rules | loans, contributions, budgets, etc. |
| 5   | UI Convenience Rules | interface behavior only, never overrides core logic |

**Interpretation**

- a screen cannot permit something that a financial rule forbids
- a module cannot bypass Chama governance rules
- a convenience setting cannot weaken audit integrity
- a cached metric cannot override actual source truth

**5.3 TENANT OWNERSHIP CANONICAL RULE**

**Rule**

Every tenant-owned record must belong to exactly one Chama.

**Implications**

- no record can move silently between Chamas
- no aggregate business action may combine Chamas unless explicit platform-admin cross-tenant reporting is authorized
- all derived objects inherit the Chama from their parent context

**Examples**

- a contribution payment created for member MB-0001 must stamp the same Chama as MB-0001
- a guarantor record must share the Chama of the parent loan
- a meeting agenda item linked to a disbursement must be in the same Chama as the meeting

**Validation Pseudocode**

def ensure_same_chama(\*records):  
chamas = {r.chama for r in records if getattr(r, "chama", None)}  
if len(chamas) > 1:  
frappe.throw("Cross-Chama linkage is not allowed")

**5.4 CANONICAL MEMBER ELIGIBILITY RULES**

These rules determine whether a member is eligible for actions across modules.

**5.4.1 General Participation Eligibility**

A member may generally participate in Chama activities only if:

- member record exists
- member belongs to active Chama
- member status permits action
- action-specific restrictions do not block participation

**5.4.2 Voting Eligibility**

Default rule:

voting_eligible =  
member.status == Active  
AND member not suspended from governance  
AND member belongs to proposal.chama

Optional Chama-specific additions:

- minimum tenure met
- no disciplinary suspension
- dues compliance threshold met

**5.4.3 Loan Eligibility**

Canonical baseline:

loan_eligible =  
member.status == Active  
AND no blocking disciplinary restriction  
AND minimum tenure met  
AND contribution/compliance rules satisfied  
AND product-specific rules satisfied

**5.4.4 Contribution Eligibility**

For recurring obligations:

contribution_eligible =  
member.status in \[Active\]  
OR member.status in \[Dormant\] if Chama policy allows

**5.4.5 Meeting/Quorum Eligibility**

Eligible attendee population defaults to:

eligible_attendees = all Active members in Chama

unless a committee-restricted meeting says otherwise.

**5.5 CANONICAL STATUS EFFECT MATRIX**

The same member status must be interpreted consistently across all modules.

| **Member Status** | **Contributions** | **Loans** | **Voting** | **Meetings** | **Investments** | **Exit** |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | no normal obligations | ineligible | ineligible | not counted | no ownership changes unless imported/setup | not applicable |
| Active | eligible | eligible | eligible | counted | eligible | can initiate |
| Suspended | existing obligations persist; new generation configurable | ineligible | ineligible | not counted for normal voting eligibility unless policy says otherwise | retains ownership but no new participation | can be processed |
| Dormant | configurable obligations | usually ineligible | usually ineligible | usually not counted | retains ownership | can reactivate/exit |
| Exit In Progress | no new obligations | ineligible | ineligible | readonly participation only | ownership subject to settlement policy | in process |
| Exited | historical only | ineligible | ineligible | historical only | no new changes except historical settlement handling | final |
| Rejected | no active participation | ineligible | ineligible | none | none | none |
| Deceased | special handling | no new actions | no voting | none | estate/beneficiary handling policy | special closure |

This matrix is canonical.

**5.6 CANONICAL CONTRIBUTION FORMULAS**

These formulas must be used consistently across Contributions, Loans, Analytics, Statements, and Settlement.

**5.6.1 Obligation Outstanding**

obligation_outstanding =  
amount_due - amount_paid - amount_waived

Constraint:

obligation_outstanding >= 0

**5.6.2 Contribution Compliance Rate**

contribution_compliance_rate =  
total_paid / total_due

**Notes**

- denominator must be explicit for selected period/filter
- if denominator = 0, compliance rate shall return:
    - null / not applicable
    - or 0 only if metric definition explicitly says so

**5.6.3 Contribution Collection Rate**

collection_rate =  
cash_collected_in_period / obligations_due_in_period

Not necessarily identical to compliance if back-payments or future prepayments exist.

**5.6.4 Overdue Days**

overdue_days =  
today - grace_end_date

only when:

amount_outstanding > 0 and today > grace_end_date

**5.6.5 Oldest-First Allocation Rule**

Default canonical allocation sequence:

1.  overdue obligations
2.  due obligations
3.  partially paid open obligations (oldest outstanding first)
4.  future obligations only if policy permits
5.  unapplied credit if excess remains

No UI or API may silently allocate differently without explicit manual allocation mode.

**5.7 CANONICAL LOAN FORMULAS**

These formulas must be consistent across Loans, Analytics, Member Statements, Settlement, and Risk dashboards.

**5.7.1 Maximum Eligible Loan**

Baseline example formula:

max_eligible_loan =  
min(  
shares_balance \* product_shares_multiplier,  
contribution_score \* product_score_factor,  
product_cap  
)

**Notes**

- exact product-specific terms may vary by Chama settings
- regardless of UI presentation, final calculation must be server-side and snapshotted

**5.7.2 Outstanding Loan Balance**

Canonical value comes from the authoritative Lending source plus permitted overlays.

At reporting level:

loan_outstanding_balance =  
principal_outstanding + interest_outstanding + charges_outstanding

or, if product/report chooses principal-only view, that must be labeled explicitly.

**5.7.3 Repayment Rate**

repayment_rate =  
amount_repaid / amount_due_for_repayment

**5.7.4 Default Rate**

Recommended default:

default_rate =  
defaulted_loans_count / total_relevant_loans_count

The denominator must be explicitly defined per report:

- active loans
- issued loans in period
- total portfolio loans

No report may change denominator silently.

**5.7.5 Guarantor Sufficiency**

guarantor_sufficiency =  
sum(confirmed_guarantee_amounts) >= required_guarantee_amount

**5.8 CANONICAL DISBURSEMENT FORMULAS**

These formulas affect Disbursements, Reconciliation, Budgeting, and Statements.

**5.8.1 Executable Amount**

executable_amount =  
approved_amount

unless partial payout mode is explicitly enabled.

**5.8.2 Budget Remaining**

budget_remaining =  
allocated_amount - actual_amount

**5.8.3 Projected Spend on Approval/Execution**

projected_actual =  
current_actual + proposed_disbursement_amount

**5.8.4 Overrun Amount**

overrun_amount =  
max(0, projected_actual - allocated_amount)

**5.9 CANONICAL RECONCILIATION FORMULAS**

This is one of the most sensitive areas.

**5.9.1 Expected Balance**

Expected Balance =  
Opening Balance  
\+ Contribution Payments Received  
\+ Loan Repayments Received  
\+ Investment Returns Received  
\+ Other Approved Inflows  
\- Disbursements Executed  
\- Loan Disbursements Executed  
\- Investment Outflows Executed  
\- Other Approved Outflows  
± Posted Adjustments

This exact logic is authoritative unless extended by documented new inflow/outflow classes.

**5.9.2 Actual Balance**

Actual Balance =  
sum(actual balances from all configured holding sources)

**5.9.3 Variance**

Variance = Actual Balance - Expected Balance

**5.9.4 Source Variance**

For each source:

source_variance = source_actual - source_expected

Even if total variance nets to zero, source-level variance remains material and must be preserved.

**5.9.5 Closing Balance**

For a closed period:

closing_balance = opening_balance + inflows - outflows ± adjustments

Where this differs from actual balance, reconciliation state must explain why.

**5.10 CANONICAL MEMBER SETTLEMENT FORMULAS**

This section must govern Member Lifecycle, Investments, Loans, Contributions, and Disbursements during exit.

**5.10.1 Baseline Settlement Formula**

Final Payout =  
shares_balance  
\+ contribution_balance  
\+ investment_entitlement_payable_now  
\+ other_adjustments  
\- loan_outstanding  
\- penalties_outstanding  
\- benefit_offsets

**5.10.2 Investment Entitlement Payable Now**

This is not automatically equal to total investment entitlement.

investment_entitlement_payable_now =  
f(total_investment_entitlement, liquidity_policy, realization_state)

Examples:

- Hold policy → 0 payable now
- Realized only → realized component only
- Manual → determined by approved settlement decision

**5.10.3 Exit Blocking Conditions**

A member may be blocked from final exit when:

- loan outstanding > 0 and policy requires full settlement
- guarantor exposure unresolved and policy = block
- ownership transfer required and not completed
- settlement approval not completed

**5.11 CANONICAL INVESTMENT FORMULAS**

These formulas must be consistent across Investment Management, Member Settlement, Analytics, and Statements.

**5.11.1 Ownership Percentage**

**Contribution Model**

ownership_percent =  
member_contributed_amount / total_contributed_amount \* 100

**Equal Model**

ownership_percent =  
100 / number_of_active_owners

**Unitized Model**

ownership_percent =  
member_units / total_units \* 100

**5.11.2 Unrealized Gain/Loss**

unrealized_gain_loss =  
current_valuation - acquisition_cost

**5.11.3 Member Entitlement Value**

member_entitlement_value =  
current_valuation \* ownership_percent / 100

**5.11.4 Return Distribution Amount**

distribution_amount =  
net_return_amount \* ownership_percent_snapshot / 100

The snapshot at event time is authoritative.

**5.12 CANONICAL GOVERNANCE FORMULAS**

These formulas govern Meetings and Voting.

**5.12.1 Attendance Rate**

attendance_rate =  
present_count / eligible_attendee_count

**5.12.2 Quorum Achievement**

**Count Mode**

quorum_achieved =  
present_or_vote_count >= quorum_required_count

**Percent Mode**

quorum_achieved =  
present_or_vote_count / eligible_population_count \* 100 >= quorum_required_percent

**5.12.3 Voting Participation Rate**

voting_participation_rate =  
actual_vote_count / eligible_voter_count

**5.12.4 Simple Majority Outcome**

approved if yes_count > no_count

**5.12.5 Absolute Majority Outcome**

approved if yes_count > 50% of eligible_voter_count

**5.12.6 Weighted Vote Outcome**

approved if yes_weight > no_weight

If ties occur, tie-break policy must be explicit.

**5.13 CANONICAL BUDGET FORMULAS**

These formulas govern Budgeting, Disbursements, Analytics, and Financial Overview.

**5.13.1 Budget Remaining**

remaining_amount = allocated_amount - actual_amount

**5.13.2 Utilization Percent**

utilization_percent =  
actual_amount / allocated_amount \* 100

**5.13.3 Budget Variance**

budget_variance =  
actual_amount - allocated_amount

**5.13.4 Budget Compliance Rate**

budget_compliance_rate =  
number_of_lines_without_overrun / total_active_budget_lines

**5.14 CANONICAL REPORTING RULES**

This is where many systems drift. We lock it here.

**5.14.1 Same Formula, Same Number Rule**

If the same metric code appears in:

- dashboard card
- report
- export
- statement
- API

then it must resolve to the same number for the same filters/context.

**5.14.2 Statement Consistency Rule**

Member statement totals must agree with:

- contributions module filtered totals
- loan module filtered totals
- investment entitlement snapshots
- settlement calculations where applicable

**5.14.3 Reconciliation Supremacy for Closing Statements**

For period-end Chama statements:

- reconciliation-approved closing balance is the authoritative period close balance
- if operational dashboards are newer, they must be labeled as live/current, not as closed-period truth

**5.15 CANONICAL DATE / PERIOD RULES**

**5.15.1 Effective Date vs Entry Date**

Every financially material record may need both:

- event/effective date
- created/entered timestamp

Reports must specify which one they use.

**5.15.2 Period Assignment Rule**

By default, period-based reporting should use:

- the effective financial/event date  
    not the create timestamp,  
    unless the report is explicitly operational-entry based.

**5.15.3 Closed Period Rule**

Records affecting closed periods:

- cannot silently mutate prior statements
- must either:
    - use approved reopen policy
    - or create correction/adjustment in a later open period with traceability

**5.16 CANONICAL ADJUSTMENT RULES**

This applies to contributions, disbursements, reconciliation, and other financially sensitive corrections.

**Rule**

No financially material historical record may be “fixed” by destructive edit if that would alter audit truth.

Approved correction patterns:

- reversal
- compensating record
- adjustment entry
- amendment workflow

Not approved:

- hard delete
- silent overwrite
- report-only correction with no source record

**5.17 CANONICAL PRIORITY OF SOURCE TRUTH**

Where multiple records might appear to describe the same thing, source truth must be defined.

| **Domain** | **Source of Truth** |
| --- | --- |
| Loan lifecycle and balances | Frappe Lending core + approved Chama extensions |
| Contribution obligation status | Chama Contribution Obligation |
| Contribution payment receipt | Chama Contribution Payment + allocations |
| Disbursement execution | Chama Disbursement Execution or authoritative Lending disbursement for loans |
| Closed-period balance | Reconciliation-approved statement snapshot |
| Member status | Chama Member |
| Meeting official record | Chama Meeting + published minutes |
| Resolution outcome | Chama Resolution |
| Budget actuals | Budget Utilization derived from executed outflows |
| Current investment value | latest Applied valuation |

Any derived cache or dashboard must defer to these sources.

**5.18 CROSS-MODULE RULE PRECEDENCE CASES**

These cases clarify tricky conflicts.

**Case 1: Member is Active in one Chama and Suspended in another**

Interpretation:

- rights are Chama-specific
- actions allowed only in the Active Chama

**Case 2: Loan module says member is eligible, but Member Lifecycle says Suspended**

Interpretation:

- Member Lifecycle status wins
- loan action blocked

**Case 3: Budget allows spend, but Disbursement approval not complete**

Interpretation:

- approval rule wins
- spend blocked until approval

**Case 4: Proposal approved but no quorum achieved**

Interpretation:

- if quorum is mandatory, result is Invalid, not Approved

**Case 5: Reconciliation live view differs from closed-period statement**

Interpretation:

- closed statement remains historical truth for that period
- live view must be labeled as post-close/current

**5.19 CROSS-MODULE EVENT TRIGGERS**

These event rules must be consistent.

| **Source Event** | **Downstream Trigger** |
| --- | --- |
| Member activated | eligibility recalculation, possible contribution generation, notification |
| Contribution payment allocated | contribution status update, analytics refresh, receipt notification |
| Loan approved | disbursement readiness, borrower notification |
| Disbursement executed | reconciliation expected balance update, budget utilization update |
| Meeting scheduled | reminders queued |
| Proposal opened | voting notifications queued |
| Budget activated | disbursement budget checks enabled |
| Investment valuation applied | entitlement refresh, analytics refresh |
| Exit settlement closed | member status changed to Exited, final statement snapshot |

**5.20 CROSS-MODULE DATA INTEGRITY INVARIANTS**

These must always be true.

1.  Every tenant-owned record has a valid chama.
2.  Every member-linked record references a member in the same Chama.
3.  Every financial execution can be traced to an approved basis or explanatory adjustment.
4.  No approved resolution exists without a final tally and recorded quorum result.
5.  No final exit exists without a settlement record.
6.  No current investment value exists without an applied valuation or acquisition baseline.
7.  No budget actual exists without a linked actual spend event.
8.  No statement snapshot may reference deleted source truth.

**5.21 VALIDATION AND RECOMPUTATION RULES**

**5.21.1 Real-Time Recompute**

Must happen immediately on save/submit for:

- contribution outstanding
- budget actual/remaining
- vote tally on close
- quorum recalculation after attendance change
- member status effect changes

**5.21.2 Scheduled Recompute**

May happen in background for:

- overdue status refresh
- risk metrics
- cached dashboard metrics
- action item overdue flags
- reminder generation

**5.21.3 Rebuildability Rule**

All derived values must be rebuildable from authoritative source records.

**5.22 ERROR HANDLING PRECEDENCE**

When a user action fails, the platform should return the most material blocking reason.

Priority:

1.  security / Chama access violation
2.  invalid state transition
3.  financial integrity conflict
4.  governance approval missing
5.  validation/data entry error
6.  UI-level convenience warning

This prevents confusing error ordering.

**5.23 AUDIT INVARIANTS**

The following actions must always create audit evidence:

- status changes
- approvals / rejections
- reversals
- adjustments
- exports of sensitive reports
- context switches for platform-level support access
- role assignments
- settlement finalization
- valuation application
- resolution enforcement

**5.24 PERFORMANCE CONSISTENCY RULE**

If a metric/report moves from live to cached mode for performance:

- formula must remain unchanged
- freshness metadata must be exposed
- ability to reconcile cached number back to source logic must remain

Performance optimization must never change business meaning.

**5.25 SECTION 5 SUMMARY RULE**

If any developer, analyst, implementer, or report author is unsure how to calculate or interpret a cross-module number:

this section is the authoritative reference.

No module-specific shortcut may override it without a documented change here.

## SECTION 5: CROSS-MODULE RULES & CANONICAL FORMULAS

**5.1 PURPOSE OF THIS SECTION**

This section defines:

- shared formulas that all modules must use
- canonical rule precedence
- cross-module state dependencies
- common financial interpretations
- conflict resolution rules when multiple modules affect the same business object
- platform-wide behavioral invariants

These rules are mandatory for:

- UI logic
- API responses
- background jobs
- reports
- exports
- statements
- audits

No module may redefine these formulas independently.

**5.2 CANONICAL RULE HIERARCHY**

When rules conflict, the system shall resolve them in this order:

| **Priority** | **Rule Source** | **Description** |
| --- | --- | --- |
| 1   | Platform Safety Rules | non-negotiable technical/security/audit rules |
| 2   | Chama Constitutional / Governance Rules | voting, approval, quorum, role authority |
| 3   | Financial Integrity Rules | no-delete, reconciliation, settlement correctness |
| 4   | Module-Specific Rules | loans, contributions, budgets, etc. |
| 5   | UI Convenience Rules | interface behavior only, never overrides core logic |

**Interpretation**

- a screen cannot permit something that a financial rule forbids
- a module cannot bypass Chama governance rules
- a convenience setting cannot weaken audit integrity
- a cached metric cannot override actual source truth

**5.3 TENANT OWNERSHIP CANONICAL RULE**

**Rule**

Every tenant-owned record must belong to exactly one Chama.

**Implications**

- no record can move silently between Chamas
- no aggregate business action may combine Chamas unless explicit platform-admin cross-tenant reporting is authorized
- all derived objects inherit the Chama from their parent context

**Examples**

- a contribution payment created for member MB-0001 must stamp the same Chama as MB-0001
- a guarantor record must share the Chama of the parent loan
- a meeting agenda item linked to a disbursement must be in the same Chama as the meeting

**Validation Pseudocode**

def ensure_same_chama(\*records):  
chamas = {r.chama for r in records if getattr(r, "chama", None)}  
if len(chamas) > 1:  
frappe.throw("Cross-Chama linkage is not allowed")

**5.4 CANONICAL MEMBER ELIGIBILITY RULES**

These rules determine whether a member is eligible for actions across modules.

**5.4.1 General Participation Eligibility**

A member may generally participate in Chama activities only if:

- member record exists
- member belongs to active Chama
- member status permits action
- action-specific restrictions do not block participation

**5.4.2 Voting Eligibility**

Default rule:

voting_eligible =  
member.status == Active  
AND member not suspended from governance  
AND member belongs to proposal.chama

Optional Chama-specific additions:

- minimum tenure met
- no disciplinary suspension
- dues compliance threshold met

**5.4.3 Loan Eligibility**

Canonical baseline:

loan_eligible =  
member.status == Active  
AND no blocking disciplinary restriction  
AND minimum tenure met  
AND contribution/compliance rules satisfied  
AND product-specific rules satisfied

**5.4.4 Contribution Eligibility**

For recurring obligations:

contribution_eligible =  
member.status in \[Active\]  
OR member.status in \[Dormant\] if Chama policy allows

**5.4.5 Meeting/Quorum Eligibility**

Eligible attendee population defaults to:

eligible_attendees = all Active members in Chama

unless a committee-restricted meeting says otherwise.

**5.5 CANONICAL STATUS EFFECT MATRIX**

The same member status must be interpreted consistently across all modules.

| **Member Status** | **Contributions** | **Loans** | **Voting** | **Meetings** | **Investments** | **Exit** |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | no normal obligations | ineligible | ineligible | not counted | no ownership changes unless imported/setup | not applicable |
| Active | eligible | eligible | eligible | counted | eligible | can initiate |
| Suspended | existing obligations persist; new generation configurable | ineligible | ineligible | not counted for normal voting eligibility unless policy says otherwise | retains ownership but no new participation | can be processed |
| Dormant | configurable obligations | usually ineligible | usually ineligible | usually not counted | retains ownership | can reactivate/exit |
| Exit In Progress | no new obligations | ineligible | ineligible | readonly participation only | ownership subject to settlement policy | in process |
| Exited | historical only | ineligible | ineligible | historical only | no new changes except historical settlement handling | final |
| Rejected | no active participation | ineligible | ineligible | none | none | none |
| Deceased | special handling | no new actions | no voting | none | estate/beneficiary handling policy | special closure |

This matrix is canonical.

**5.6 CANONICAL CONTRIBUTION FORMULAS**

These formulas must be used consistently across Contributions, Loans, Analytics, Statements, and Settlement.

**5.6.1 Obligation Outstanding**

obligation_outstanding =  
amount_due - amount_paid - amount_waived

Constraint:

obligation_outstanding >= 0

**5.6.2 Contribution Compliance Rate**

contribution_compliance_rate =  
total_paid / total_due

**Notes**

- denominator must be explicit for selected period/filter
- if denominator = 0, compliance rate shall return:
    - null / not applicable
    - or 0 only if metric definition explicitly says so

**5.6.3 Contribution Collection Rate**

collection_rate =  
cash_collected_in_period / obligations_due_in_period

Not necessarily identical to compliance if back-payments or future prepayments exist.

**5.6.4 Overdue Days**

overdue_days =  
today - grace_end_date

only when:

amount_outstanding > 0 and today > grace_end_date

**5.6.5 Oldest-First Allocation Rule**

Default canonical allocation sequence:

1.  overdue obligations
2.  due obligations
3.  partially paid open obligations (oldest outstanding first)
4.  future obligations only if policy permits
5.  unapplied credit if excess remains

No UI or API may silently allocate differently without explicit manual allocation mode.

**5.7 CANONICAL LOAN FORMULAS**

These formulas must be consistent across Loans, Analytics, Member Statements, Settlement, and Risk dashboards.

**5.7.1 Maximum Eligible Loan**

Baseline example formula:

max_eligible_loan =  
min(  
shares_balance \* product_shares_multiplier,  
contribution_score \* product_score_factor,  
product_cap  
)

**Notes**

- exact product-specific terms may vary by Chama settings
- regardless of UI presentation, final calculation must be server-side and snapshotted

**5.7.2 Outstanding Loan Balance**

Canonical value comes from the authoritative Lending source plus permitted overlays.

At reporting level:

loan_outstanding_balance =  
principal_outstanding + interest_outstanding + charges_outstanding

or, if product/report chooses principal-only view, that must be labeled explicitly.

**5.7.3 Repayment Rate**

repayment_rate =  
amount_repaid / amount_due_for_repayment

**5.7.4 Default Rate**

Recommended default:

default_rate =  
defaulted_loans_count / total_relevant_loans_count

The denominator must be explicitly defined per report:

- active loans
- issued loans in period
- total portfolio loans

No report may change denominator silently.

**5.7.5 Guarantor Sufficiency**

guarantor_sufficiency =  
sum(confirmed_guarantee_amounts) >= required_guarantee_amount

**5.8 CANONICAL DISBURSEMENT FORMULAS**

These formulas affect Disbursements, Reconciliation, Budgeting, and Statements.

**5.8.1 Executable Amount**

executable_amount =  
approved_amount

unless partial payout mode is explicitly enabled.

**5.8.2 Budget Remaining**

budget_remaining =  
allocated_amount - actual_amount

**5.8.3 Projected Spend on Approval/Execution**

projected_actual =  
current_actual + proposed_disbursement_amount

**5.8.4 Overrun Amount**

overrun_amount =  
max(0, projected_actual - allocated_amount)

**5.9 CANONICAL RECONCILIATION FORMULAS**

This is one of the most sensitive areas.

**5.9.1 Expected Balance**

Expected Balance =  
Opening Balance  
\+ Contribution Payments Received  
\+ Loan Repayments Received  
\+ Investment Returns Received  
\+ Other Approved Inflows  
\- Disbursements Executed  
\- Loan Disbursements Executed  
\- Investment Outflows Executed  
\- Other Approved Outflows  
± Posted Adjustments

This exact logic is authoritative unless extended by documented new inflow/outflow classes.

**5.9.2 Actual Balance**

Actual Balance =  
sum(actual balances from all configured holding sources)

**5.9.3 Variance**

Variance = Actual Balance - Expected Balance

**5.9.4 Source Variance**

For each source:

source_variance = source_actual - source_expected

Even if total variance nets to zero, source-level variance remains material and must be preserved.

**5.9.5 Closing Balance**

For a closed period:

closing_balance = opening_balance + inflows - outflows ± adjustments

Where this differs from actual balance, reconciliation state must explain why.

**5.10 CANONICAL MEMBER SETTLEMENT FORMULAS**

This section must govern Member Lifecycle, Investments, Loans, Contributions, and Disbursements during exit.

**5.10.1 Baseline Settlement Formula**

Final Payout =  
shares_balance  
\+ contribution_balance  
\+ investment_entitlement_payable_now  
\+ other_adjustments  
\- loan_outstanding  
\- penalties_outstanding  
\- benefit_offsets

**5.10.2 Investment Entitlement Payable Now**

This is not automatically equal to total investment entitlement.

investment_entitlement_payable_now =  
f(total_investment_entitlement, liquidity_policy, realization_state)

Examples:

- Hold policy → 0 payable now
- Realized only → realized component only
- Manual → determined by approved settlement decision

**5.10.3 Exit Blocking Conditions**

A member may be blocked from final exit when:

- loan outstanding > 0 and policy requires full settlement
- guarantor exposure unresolved and policy = block
- ownership transfer required and not completed
- settlement approval not completed

**5.11 CANONICAL INVESTMENT FORMULAS**

These formulas must be consistent across Investment Management, Member Settlement, Analytics, and Statements.

**5.11.1 Ownership Percentage**

**Contribution Model**

ownership_percent =  
member_contributed_amount / total_contributed_amount \* 100

**Equal Model**

ownership_percent =  
100 / number_of_active_owners

**Unitized Model**

ownership_percent =  
member_units / total_units \* 100

**5.11.2 Unrealized Gain/Loss**

unrealized_gain_loss =  
current_valuation - acquisition_cost

**5.11.3 Member Entitlement Value**

member_entitlement_value =  
current_valuation \* ownership_percent / 100

**5.11.4 Return Distribution Amount**

distribution_amount =  
net_return_amount \* ownership_percent_snapshot / 100

The snapshot at event time is authoritative.

**5.12 CANONICAL GOVERNANCE FORMULAS**

These formulas govern Meetings and Voting.

**5.12.1 Attendance Rate**

attendance_rate =  
present_count / eligible_attendee_count

**5.12.2 Quorum Achievement**

**Count Mode**

quorum_achieved =  
present_or_vote_count >= quorum_required_count

**Percent Mode**

quorum_achieved =  
present_or_vote_count / eligible_population_count \* 100 >= quorum_required_percent

**5.12.3 Voting Participation Rate**

voting_participation_rate =  
actual_vote_count / eligible_voter_count

**5.12.4 Simple Majority Outcome**

approved if yes_count > no_count

**5.12.5 Absolute Majority Outcome**

approved if yes_count > 50% of eligible_voter_count

**5.12.6 Weighted Vote Outcome**

approved if yes_weight > no_weight

If ties occur, tie-break policy must be explicit.

**5.13 CANONICAL BUDGET FORMULAS**

These formulas govern Budgeting, Disbursements, Analytics, and Financial Overview.

**5.13.1 Budget Remaining**

remaining_amount = allocated_amount - actual_amount

**5.13.2 Utilization Percent**

utilization_percent =  
actual_amount / allocated_amount \* 100

**5.13.3 Budget Variance**

budget_variance =  
actual_amount - allocated_amount

**5.13.4 Budget Compliance Rate**

budget_compliance_rate =  
number_of_lines_without_overrun / total_active_budget_lines

**5.14 CANONICAL REPORTING RULES**

This is where many systems drift. We lock it here.

**5.14.1 Same Formula, Same Number Rule**

If the same metric code appears in:

- dashboard card
- report
- export
- statement
- API

then it must resolve to the same number for the same filters/context.

**5.14.2 Statement Consistency Rule**

Member statement totals must agree with:

- contributions module filtered totals
- loan module filtered totals
- investment entitlement snapshots
- settlement calculations where applicable

**5.14.3 Reconciliation Supremacy for Closing Statements**

For period-end Chama statements:

- reconciliation-approved closing balance is the authoritative period close balance
- if operational dashboards are newer, they must be labeled as live/current, not as closed-period truth

**5.15 CANONICAL DATE / PERIOD RULES**

**5.15.1 Effective Date vs Entry Date**

Every financially material record may need both:

- event/effective date
- created/entered timestamp

Reports must specify which one they use.

**5.15.2 Period Assignment Rule**

By default, period-based reporting should use:

- the effective financial/event date  
    not the create timestamp,  
    unless the report is explicitly operational-entry based.

**5.15.3 Closed Period Rule**

Records affecting closed periods:

- cannot silently mutate prior statements
- must either:
    - use approved reopen policy
    - or create correction/adjustment in a later open period with traceability

**5.16 CANONICAL ADJUSTMENT RULES**

This applies to contributions, disbursements, reconciliation, and other financially sensitive corrections.

**Rule**

No financially material historical record may be “fixed” by destructive edit if that would alter audit truth.

Approved correction patterns:

- reversal
- compensating record
- adjustment entry
- amendment workflow

Not approved:

- hard delete
- silent overwrite
- report-only correction with no source record

**5.17 CANONICAL PRIORITY OF SOURCE TRUTH**

Where multiple records might appear to describe the same thing, source truth must be defined.

| **Domain** | **Source of Truth** |
| --- | --- |
| Loan lifecycle and balances | Frappe Lending core + approved Chama extensions |
| Contribution obligation status | Chama Contribution Obligation |
| Contribution payment receipt | Chama Contribution Payment + allocations |
| Disbursement execution | Chama Disbursement Execution or authoritative Lending disbursement for loans |
| Closed-period balance | Reconciliation-approved statement snapshot |
| Member status | Chama Member |
| Meeting official record | Chama Meeting + published minutes |
| Resolution outcome | Chama Resolution |
| Budget actuals | Budget Utilization derived from executed outflows |
| Current investment value | latest Applied valuation |

Any derived cache or dashboard must defer to these sources.

**5.18 CROSS-MODULE RULE PRECEDENCE CASES**

These cases clarify tricky conflicts.

**Case 1: Member is Active in one Chama and Suspended in another**

Interpretation:

- rights are Chama-specific
- actions allowed only in the Active Chama

**Case 2: Loan module says member is eligible, but Member Lifecycle says Suspended**

Interpretation:

- Member Lifecycle status wins
- loan action blocked

**Case 3: Budget allows spend, but Disbursement approval not complete**

Interpretation:

- approval rule wins
- spend blocked until approval

**Case 4: Proposal approved but no quorum achieved**

Interpretation:

- if quorum is mandatory, result is Invalid, not Approved

**Case 5: Reconciliation live view differs from closed-period statement**

Interpretation:

- closed statement remains historical truth for that period
- live view must be labeled as post-close/current

**5.19 CROSS-MODULE EVENT TRIGGERS**

These event rules must be consistent.

| **Source Event** | **Downstream Trigger** |
| --- | --- |
| Member activated | eligibility recalculation, possible contribution generation, notification |
| Contribution payment allocated | contribution status update, analytics refresh, receipt notification |
| Loan approved | disbursement readiness, borrower notification |
| Disbursement executed | reconciliation expected balance update, budget utilization update |
| Meeting scheduled | reminders queued |
| Proposal opened | voting notifications queued |
| Budget activated | disbursement budget checks enabled |
| Investment valuation applied | entitlement refresh, analytics refresh |
| Exit settlement closed | member status changed to Exited, final statement snapshot |

**5.20 CROSS-MODULE DATA INTEGRITY INVARIANTS**

These must always be true.

1.  Every tenant-owned record has a valid chama.
2.  Every member-linked record references a member in the same Chama.
3.  Every financial execution can be traced to an approved basis or explanatory adjustment.
4.  No approved resolution exists without a final tally and recorded quorum result.
5.  No final exit exists without a settlement record.
6.  No current investment value exists without an applied valuation or acquisition baseline.
7.  No budget actual exists without a linked actual spend event.
8.  No statement snapshot may reference deleted source truth.

**5.21 VALIDATION AND RECOMPUTATION RULES**

**5.21.1 Real-Time Recompute**

Must happen immediately on save/submit for:

- contribution outstanding
- budget actual/remaining
- vote tally on close
- quorum recalculation after attendance change
- member status effect changes

**5.21.2 Scheduled Recompute**

May happen in background for:

- overdue status refresh
- risk metrics
- cached dashboard metrics
- action item overdue flags
- reminder generation

**5.21.3 Rebuildability Rule**

All derived values must be rebuildable from authoritative source records.

**5.22 ERROR HANDLING PRECEDENCE**

When a user action fails, the platform should return the most material blocking reason.

Priority:

1.  security / Chama access violation
2.  invalid state transition
3.  financial integrity conflict
4.  governance approval missing
5.  validation/data entry error
6.  UI-level convenience warning

This prevents confusing error ordering.

**5.23 AUDIT INVARIANTS**

The following actions must always create audit evidence:

- status changes
- approvals / rejections
- reversals
- adjustments
- exports of sensitive reports
- context switches for platform-level support access
- role assignments
- settlement finalization
- valuation application
- resolution enforcement

**5.24 PERFORMANCE CONSISTENCY RULE**

If a metric/report moves from live to cached mode for performance:

- formula must remain unchanged
- freshness metadata must be exposed
- ability to reconcile cached number back to source logic must remain

Performance optimization must never change business meaning.

**5.25 SECTION 5 SUMMARY RULE**

If any developer, analyst, implementer, or report author is unsure how to calculate or interpret a cross-module number:

this section is the authoritative reference.

No module-specific shortcut may override it without a documented change here.

## SECTION 6: API STANDARDS, SECURITY, AND INTEGRATION RULES

**6.1 PURPOSE OF THIS SECTION**

This section defines the mandatory standards for:

- API design
- request and response formats
- authentication and authorization
- tenant-safe API access
- mobile app integration
- web client interaction rules
- background/system integrations
- error handling conventions
- idempotency requirements
- rate limiting and abuse protection
- audit and traceability of integrations

These rules apply to:

- custom Frappe whitelisted methods
- /api/resource/\* usage where allowed
- internal service calls
- mobile client calls
- admin/support tooling
- future third-party integrations

No endpoint may ignore this section.

**6.2 API ARCHITECTURE PRINCIPLES**

The system shall follow these principles:

1.  **Reuse Frappe/ERPNext standard API mechanisms where safe**
2.  **Use custom whitelisted methods for business actions**
3.  **Never expose direct raw data access when business rules must be enforced**
4.  **Tenant safety must be enforced server-side**
5.  **APIs must be explicit about context, validation, and side effects**
6.  **All state-changing endpoints must be auditable**
7.  **Idempotency must be supported for high-risk financial actions**

**6.3 API CATEGORIES**

The platform shall recognize four categories of APIs.

| **Category** | **Purpose** | **Examples** |
| --- | --- | --- |
| Read APIs | fetch data without changing state | dashboard data, profile view, list reports |
| Action APIs | execute business actions | apply loan, submit vote, execute disbursement |
| Admin APIs | tenant/platform administration | create Chama, archive Chama |
| Internal/System APIs | background jobs, worker integrations, callbacks | queue processing, reminder generation |

**6.4 API DESIGN RULES**

**6.4.1 Read vs Action Separation**

Read endpoints must not mutate state.

Action endpoints must not be disguised as reads.

**Allowed**

- GET /api/method/chama.member.profile
- POST /api/method/chama.loan.apply

**Not allowed**

- a GET endpoint that marks notifications as read
- a report endpoint that silently recalculates and posts adjustments

**6.4.2 Endpoint Naming Convention**

Custom method endpoints shall use a namespaced convention:

/api/method/chama.&lt;module&gt;.&lt;action&gt;

Examples:

- /api/method/chama.loan.apply
- /api/method/chama.contribution.submit_payment
- /api/method/chama.meeting.close
- /api/method/chama.analytics.generate_report

This keeps the API surface organized and predictable.

**6.4.3 Resource API Usage Rule**

Use /api/resource/&lt;DocType&gt; only when:

- read/write behavior is simple
- no complex business logic is bypassed
- no financial or governance action is being performed

**Suitable examples**

- reading a published meeting record
- reading a member’s own notification inbox row

**Not suitable examples**

- approving a loan
- allocating a payment
- applying a valuation
- finalizing a settlement

Those must go through action APIs.

**6.5 REQUEST AND RESPONSE STANDARDS**

**6.5.1 Standard Success Response**

All custom APIs shall return:

{  
"status": "success",  
"data": {},  
"errors": \[\]  
}

**6.5.2 Standard Error Response**

All custom APIs shall return machine-readable errors:

{  
"status": "error",  
"data": null,  
"errors": \[  
{  
"error_code": "LN001",  
"message": "Amount exceeds eligibility",  
"details": {}  
}  
\]  
}

**6.5.3 Multi-Error Rule**

Where practical, the API may return multiple validation errors in one response.  
For stateful/financial actions, the API may stop at the first material blocking error if that improves safety and clarity.

**6.5.4 Response Metadata**

Where relevant, responses should include metadata such as:

- pagination
- last_updated
- metric freshness
- current Chama context
- drill-down route hints
- report row count

Example:

{  
"status": "success",  
"data": {  
"rows": \[\],  
"row_count": 0  
},  
"meta": {  
"page": 1,  
"page_size": 50,  
"chama": "CH-0001"  
},  
"errors": \[\]  
}

**6.6 INPUT VALIDATION RULES**

All business APIs must validate:

1.  authentication
2.  tenant access
3.  permission to perform action
4.  input schema
5.  current record state
6.  cross-module dependencies
7.  business rules
8.  financial integrity constraints

Validation must happen server-side even if the client also validates.

**6.6.1 Schema Validation**

Every endpoint must define:

- required fields
- allowed types
- enum values
- conditional required fields
- max/min constraints

**6.6.2 Unknown Field Rule**

Unknown or unsupported input fields should be:

- ignored only for explicitly tolerant APIs
- otherwise rejected to prevent silent misuse

For financial and governance actions, reject unknown critical fields.

**6.7 AUTHENTICATION RULES**

The platform shall support:

| **Auth Type** | **Use Case** |
| --- | --- |
| Session-based auth | web app / Desk |
| Token-based auth | mobile app |
| Internal trusted auth | system/background processes only |

**6.7.1 Web Authentication**

ERPNext/Frappe session-based authentication may be used for:

- Desk users
- browser sessions
- internal authorized web operations

**6.7.2 Mobile Authentication**

Mobile APIs shall use token-based authentication.

The system must support:

- secure login
- access token
- refresh token strategy if implemented
- device-aware session invalidation if required

Sensitive mobile actions should not rely only on client identity caching.

**6.7.3 Internal Worker Authentication**

Background workers and internal schedulers may operate using trusted server context, but:

- actions must still be auditable
- impersonation of end-users must be explicit if used
- tenant context must still be explicit

**6.8 AUTHORIZATION RULES**

Authentication answers **who** the caller is.  
Authorization answers **what the caller may do now, in this Chama, on this record**.

Every action endpoint must evaluate:

1.  current user
2.  active Chama context
3.  user’s member record in that Chama, if applicable
4.  Chama-specific role assignments
5.  member status
6.  record state
7.  policy and module rules

**6.8.1 Authorization Formula**

Conceptually:

authorized =  
authenticated  
AND has_access_to_chama  
AND has_required_role_or_ownership  
AND status_allows_action  
AND record_state_allows_action

**6.8.2 Ownership-Based Access**

For member-facing endpoints, access should default to:

- only own records
- only own linked items
- only own notifications
- only own statements

unless a Chama role explicitly broadens access.

**6.8.3 Role-Based Access**

Officer/admin roles may access wider data within a Chama, but only according to:

- Chama role assignment
- current Chama context
- module policy

A Treasurer in Chama A is not automatically a Treasurer in Chama B.

**6.8.4 Platform Admin Restriction**

Platform admin access must not silently bypass business authorization.

If a platform admin performs:

- cross-tenant read
- tenant support action
- export
- context override

it must be:

- explicitly authorized
- scoped
- audited

**6.9 TENANT-SAFE API RULES**

This is non-negotiable.

Every tenant-owned endpoint must:

- infer active Chama from secure session/context
- or validate explicit chama input against allowed access
- reject mismatches

**6.9.1 Context Mismatch Rule**

If request payload says chama = CH-0002 but the caller’s active context is CH-0001, the endpoint must:

- reject the request
- unless the caller is a scoped platform admin performing an audited support/admin action

**6.9.2 Cross-Tenant Link Rule**

No endpoint may accept cross-tenant references.

Example:

- member from Chama A cannot be linked to loan in Chama B
- proposal in Chama A cannot reference disbursement in Chama B

**6.10 IDEMPOTENCY RULES**

Idempotency is mandatory for high-risk actions.

**6.10.1 Actions Requiring Idempotency Support**

These must support idempotency keys or equivalent replay protection:

- contribution payment submission
- disbursement execution
- disbursement reversal
- loan application submission if external/mobile retry risk exists
- vote submission
- return distribution
- settlement payout finalization
- notification send where duplicate sends would be harmful

**6.10.2 Idempotency Key Pattern**

Example request header or body field:

Idempotency-Key: 9c3efc2b-...

The server must:

- store request fingerprint + result
- return original result if exact retry occurs
- reject conflicting replay if same key is used with different payload

**6.10.3 Conflict Replay Rule**

If the same idempotency key is reused with different business payload:

- reject request
- log security/consistency warning

**6.11 CONCURRENCY AND STATE SAFETY RULES**

Multiple users or retries may hit the same records.

The system must protect:

- voting from double submission
- payment allocation from double posting
- disbursement from double execution
- settlement from double finalization
- valuation from duplicate apply
- budget amendment from outdated version apply

**6.11.1 Optimistic Concurrency Rule**

For stateful records, the server should validate:

- current state
- current version/timestamp where useful
- that the transition is still valid at commit time

**6.11.2 Double-Execution Protection**

Before executing financial actions, the API must re-check:

- status still eligible
- no existing execution/reversal already posted
- no pending concurrent transaction already completed

**6.12 ERROR CODE CONVENTION**

Error codes must be structured and stable.

Recommended prefixes:

- AUTH authentication
- PERM authorization
- CTX context / tenant mismatch
- VAL generic validation
- LN loans
- CN contributions
- DB disbursements
- RC reconciliation
- MT meetings
- VT voting
- BG budgeting
- MB member lifecycle
- IV investments
- AN analytics
- NT notifications
- MC multi-Chama/platform controls

Example:

- CTX001
- PERM004
- DB202
- VT204

**6.12.1 Human Message Rule**

Every error must include a readable message suitable for UI display or logging.  
Sensitive internal details should go into structured details, not the top-level message.

**6.13 API VERSIONING RULES**

The initial internal implementation may use stable method namespaces without explicit public versioning, but the design must be versionable.

Recommended future pattern:

/api/method/chama.v1.loan.apply

For now, if versioning is omitted, breaking changes must be tightly controlled.

**6.13.1 Backward Compatibility Rule**

If mobile clients depend on an endpoint, breaking response schema changes must not be introduced without:

- version bump
- migration plan
- coordinated rollout

**6.14 PAGINATION, FILTERING, AND SORTING RULES**

List/report endpoints must support:

- pagination
- deterministic ordering
- explicit filters
- tenant-safe filtering defaults

**6.14.1 Required Query Controls**

Recommended standard:

- page
- page_size
- sort_by
- sort_order
- filters

**6.14.2 Safe Defaults**

If no pagination is supplied:

- return reasonable default page size
- never dump massive record sets by default for member/mobile endpoints

**6.15 MOBILE INTEGRATION RULES**

The mobile app is a first-class client for member-facing functionality.

Mobile APIs must be:

- minimal in payload
- explicit in state
- safe for intermittent connectivity
- idempotent where retries are likely
- optimized for list/detail patterns

**6.15.1 Mobile Response Design**

Mobile endpoints should prefer:

- compact payloads
- pre-computed labels/status badges where helpful
- direct next-step hints
- limited nesting unless necessary

**6.15.2 Offline / Retry Rule**

Where mobile may retry due to poor connectivity:

- payment submissions
- vote submissions
- loan applications
- read state updates

must handle safe retry semantics.

**6.15.3 Mobile Deep Link Rule**

Notification payloads and dashboard drill-downs may include route hints, but:

- server-side authorization must still be enforced on actual data fetch
- deep links must remain tenant-safe

**6.16 INTEGRATION RULES FOR EXTERNAL SYSTEMS**

This platform may later integrate with:

- SMS providers
- mobile money systems
- bank statement imports
- email providers
- external identity systems
- document storage
- analytics exports

All external integrations must go through controlled adapters, not direct module logic.

**6.16.1 Adapter Rule**

Source modules must not call third-party providers directly.  
They must invoke adapter/service layers.

Examples:

- notification engine → SMS adapter
- reconciliation import → statement import adapter
- disbursement integration → payment provider adapter

**6.16.2 Callback Validation Rule**

If external systems call back into the platform:

- signatures/tokens must be verified
- payloads validated
- idempotency enforced
- audit logs written

**6.17 WEBHOOK / EVENT INTEGRATION RULES**

If internal or external webhook/event architecture is introduced, each event must include:

- event type
- source module
- Chama
- source record reference
- event timestamp
- idempotency or unique event ID

Example:

{  
"event_id": "evt-123",  
"event_type": "disbursement_executed",  
"chama": "CH-0001",  
"source_module": "Disbursements",  
"source_doctype": "Chama Disbursement Execution",  
"source_docname": "DBX-0021",  
"occurred_at": "2026-05-01T10:00:00Z"  
}

**6.18 SECURITY RULES**

Security must be enforced at every API boundary.

**6.18.1 Input Trust Rule**

No client input is trusted by default.

The server must validate:

- field types
- allowed enums
- object ownership
- tenant consistency
- state transition validity
- numeric bounds
- business authority

**6.18.2 Sensitive Data Rule**

Sensitive fields such as:

- national ID
- phone
- financial balances
- settlement details
- audit logs
- cross-tenant admin actions

must only be returned to authorized roles.

**6.18.3 Secret Handling Rule**

The API must not expose:

- provider secrets
- internal stack traces
- raw system configuration secrets
- tokens in normal responses

**6.18.4 Support/Admin Override Rule**

Override actions must:

- be explicit
- require authority
- log actor, reason, timestamp, tenant
- never silently masquerade as user activity

**6.19 AUDIT AND TRACEABILITY RULES FOR APIs**

Every state-changing API must log:

- actor
- active Chama
- endpoint/action
- target record(s)
- before state where relevant
- after state where relevant
- timestamp
- idempotency key if used
- request correlation ID if available

This applies especially to:

- approvals
- reversals
- settlement finalization
- exports
- context overrides
- role assignment
- payout execution

**6.20 RATE LIMITING AND ABUSE PROTECTION**

The platform must support protective throttling, especially for:

- login
- OTP/token flows if used
- vote submission
- payment submission
- report generation
- export endpoints
- notification retry/admin tools

**6.20.1 Example Throttle Classes**

| **Endpoint Type** | **Suggested Behavior** |
| --- | --- |
| login/auth | aggressive throttling |
| member dashboard reads | light throttling |
| financial action APIs | moderate throttling + idempotency |
| heavy reports/exports | strict throttling or async generation |

**6.21 ASYNC AND LONG-RUNNING OPERATIONS**

Some APIs should not block waiting for heavy work.

Candidates:

- heavy report exports
- bulk notification sends
- metric refresh jobs
- large reconciliation imports
- bulk onboarding imports

For such actions:

- accept request
- create job/task record if needed
- return accepted status
- expose polling or inbox notification when done

**6.21.1 Async Response Pattern**

{  
"status": "success",  
"data": {  
"job_id": "JOB-0001",  
"job_status": "Queued"  
},  
"errors": \[\]  
}

**6.22 FILE AND ATTACHMENT RULES**

Attachments may be used by:

- disbursement support docs
- meeting minutes
- valuations
- reconciliation evidence
- reports/exports

Rules:

- attachment access must inherit tenant and role controls
- no raw public file exposure for sensitive docs
- exported statements/reports should be access-controlled
- audit-sensitive attachments should be traceable to uploader and source record

**6.23 API TESTABILITY RULES**

Every action API should be testable with:

- valid request case
- invalid permission case
- invalid state case
- tenant mismatch case
- duplicate/idempotent replay case
- audit side effect verification

The API design must make these test cases possible and deterministic.

**6.24 INTEGRATION CONSISTENCY RULES**

If an API changes business state, it must update all required downstream effects or explicitly queue them.

Examples:

- approving a loan must not forget notification event generation
- executing disbursement must not forget budget utilization and reconciliation impact
- applying valuation must not forget entitlement refresh
- finalizing exit must not forget status change log and statement generation

No endpoint may leave the system partially updated without an intentional, recoverable async pattern.

**6.25 SECTION 6 CANONICAL SECURITY/INTEGRATION INVARIANTS**

These must always be true:

1.  Every tenant-owned action validates Chama access server-side.
2.  No sensitive business action is performed through raw unrestricted resource writes.
3.  Every high-risk financial action is replay-safe or idempotent.
4.  Every state-changing API is auditable.
5.  No client-supplied status transition is trusted without server validation.
6.  No report/export may leak tenant or member data outside authorization rules.
7.  External callbacks must be authenticated and replay-protected.
8.  Mobile retry behavior must not create duplicate financial or governance actions.

## SECTION 7: WORKFLOW, SCHEDULER, AND AUTOMATION MATRIX

**7.1 PURPOSE OF THIS SECTION**

This section defines:

- formal workflow catalogue
- scheduled/background job catalogue
- automation triggers
- dependency ordering
- retry and failure handling
- job ownership and auditability
- timing semantics
- idempotency requirements for automations

These rules apply to:

- business workflows
- notifications
- reminders
- status refreshes
- reconciliation checks
- metrics refreshes
- periodic closes
- background processing queues

No automation may exist outside this section once the system is stabilized.

**7.2 AUTOMATION DESIGN PRINCIPLES**

The platform shall follow these principles:

1.  **Business workflows are explicit**
2.  **Background jobs must be idempotent**
3.  **Automations must be tenant-safe**
4.  **Automations must be auditable**
5.  **Failure must be visible**
6.  **Critical jobs must be retryable**
7.  **No automation may silently mutate historical truth**
8.  **Scheduling must respect Chama timezone semantics where relevant**
9.  **Heavy jobs must be separable from interactive user requests**
10. **Derived-state jobs must be rebuildable from source records**

**7.3 AUTOMATION CLASSES**

The platform shall recognize the following automation classes:

| **Class** | **Description** | **Examples** |
| --- | --- | --- |
| Immediate workflow transition | happens synchronously during action | submit loan, approve waiver |
| Deferred business automation | happens shortly after action | notification queueing, entitlement refresh |
| Scheduled periodic job | time-based recurring job | overdue checks, reminders |
| Batch recomputation job | refreshes derived data | metric snapshots, aging buckets |
| Exception handling job | retries or escalates failures | failed notification retries |
| Period close / governance automation | period-end or meeting lifecycle control | close proposals, archive statements |

**7.4 GLOBAL WORKFLOW CATALOGUE**

The following workflow families are canonical:

| **Workflow Family** | **Primary Module** |
| --- | --- |
| Loan Approval & Lifecycle | Loans |
| Contribution Obligation & Payment Lifecycle | Contributions |
| Disbursement Request / Execution / Reversal | Disbursements |
| Reconciliation / Adjustment / Period Close | Reconciliation |
| Notification Event / Queue / Inbox | Notifications |
| Meeting / Minutes / Action Items | Meetings |
| Proposal / Vote / Resolution | Voting |
| Budget / Amendment / Overrun Escalation | Budgeting |
| Member Application / Status / Exit / Settlement | Member Lifecycle |
| Investment Proposal / Activation / Valuation / Return Distribution | Investment |
| Chama Lifecycle / Context Control | Multi-Chama |
| Reporting / Metrics Refresh | Analytics |

**7.5 WORKFLOW MATRIX — LOANS**

**7.5.1 Loan Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| Loan submit | member submits | Member / API | eligible, valid input, guarantors selected | Draft → Submitted | create guarantors, snapshot eligibility, notify treasurer | Sync |
| Loan review open | system after submit | System | loan submitted | Submitted → Under Review | queue reviewer notification | Async/immediate |
| Loan approve | treasurer/chair | Officer | guarantor sufficient, rule checks pass | Under Review → Approved | mark ready for disbursement, notify borrower | Sync |
| Loan reject | treasurer/chair | Officer | review state valid | Under Review → Rejected | notify borrower | Sync |
| Loan disburse | lending/treasurer | Lending/System | approved, funds available | Approved → Disbursed | create mirror/report link, notify borrower | Sync + async mirrors |
| Overdue detection | scheduler | System | missed due payment | Active → Overdue | notify borrower/guarantors | Scheduled |
| Default detection | scheduler | System | overdue threshold reached | Overdue → Defaulted | risk alert, possible guarantor flow | Scheduled |
| Loan close | repayment completion | Lending/System | outstanding = 0 | Active/Overdue → Closed | release guarantors, notify | Sync/async |

**7.5.2 Loan Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| loan_overdue_refresh | Daily | per Chama | update overdue states | retry next cycle + alert if repeated |
| loan_default_check | Daily | per Chama | mark defaulted loans | retry + log |
| loan_repayment_reminder_queue | Daily / configured | per Chama | create due reminders | retry + metrics flag |
| guarantor_release_check | Daily | global/per Chama | release guarantor flags on closed loans | retry |

**7.6 WORKFLOW MATRIX — CONTRIBUTIONS**

**7.6.1 Contribution Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| cycle generation | scheduler/manual | System/Treasurer | active categories, eligible members | create cycle + obligations | due reminders later, reporting availability | Scheduled |
| due refresh | scheduler | System | due_date reached | Pending → Due | reminder event | Scheduled |
| payment submit | member/treasurer/API | Member/Treasurer | valid amount/member | create payment | allocate, receipt, metrics update | Sync |
| payment allocate | post-payment logic | System | payment recorded | Recorded → Allocated/Partially Allocated | update obligations, notify member | Sync |
| overdue refresh | scheduler | System | grace exceeded, outstanding > 0 | Due/Partial → Overdue | queue alert, penalty check | Scheduled |
| penalty apply | scheduler | System | penalty rule exists and criteria met | create penalty obligation | notify if configured | Scheduled |
| waiver submit | treasurer | Treasurer | reason present | Draft → Submitted | notify approver | Sync |
| waiver approve | chair/authorized | Officer | valid waiver | Submitted → Approved | update obligation amounts/status | Sync |
| payment reverse | treasurer/admin | Officer | reversible | Allocated → Reversed (payment) | reverse allocations, recompute | Sync |

**7.6.2 Contribution Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| contribution_cycle_generation | Daily | per Chama | create cycles/obligations | retry, alert if repeated |
| contribution_due_status_refresh | Daily | per Chama | update Pending/Due | retry |
| contribution_overdue_refresh | Daily | per Chama | update Overdue | retry |
| contribution_penalty_apply | Daily | per Chama | create penalties | retry + duplicate-safe |
| contribution_due_reminder_queue | Daily / configured | per Chama | due reminder events | retry |
| contribution_credit_cleanup_check | Daily | per Chama | identify stale unapplied credits | warn only |

**7.7 WORKFLOW MATRIX — DISBURSEMENTS**

**7.7.1 Disbursement Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| request submit | member/treasurer | User | beneficiary valid, amount valid | Draft → Submitted | budget check, approval routing, notify reviewer | Sync |
| review open | reviewer action/system | Treasurer | submitted | Submitted → Under Review | —   | Sync |
| escalation | rule engine | System/Treasurer | threshold or policy | Under Review → Pending Approval | notify higher approver | Sync |
| approval | approver | Chair/Treasurer | authority valid, checks passed | Pending/Review → Approved | mark ready for execution | Sync |
| rejection | approver | Chair/Treasurer | valid state | Pending/Review → Rejected | notify requester | Sync |
| ready for execution | system | System | approved + funds/budget OK | Approved → Ready for Execution | notify executor | Async/immediate |
| execute payout | treasurer/system | Treasurer/System | ready state valid | Ready → Executed | reconciliation effect, budget utilization, notify beneficiary | Sync + async downstream |
| execution fail | provider/manual | System/Treasurer | provider fail or invalid reference | Ready → Failed | alert ops | Sync |
| reversal | treasurer/admin | Officer | reversible | Executed → Reversed | compensating execution, audit | Sync |

**7.7.2 Disbursement Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| pending_execution_monitor | Hourly | per Chama | detect stale approved payouts | alert treasurer |
| failed_disbursement_retry_review | Hourly/Daily | per Chama | surface failed executions for retry | no auto re-execute unless safe |
| disbursement_budget_recheck | On execute + periodic stale checks | per Chama | catch pre-execution budget/fund drift | block execution |

**7.8 WORKFLOW MATRIX — RECONCILIATION & PERIOD CLOSE**

**7.8.1 Reconciliation Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| run reconciliation | treasurer/system | Treasurer | actual balances entered | create run | create issues if variance | Sync |
| issue investigate | reviewer | Treasurer/Reviewer | issue open | Open → Investigating | assign owner | Sync |
| adjustment submit | treasurer | Treasurer | reason valid, amount valid | Draft → Submitted | notify approver | Sync |
| adjustment approve | approver | Chair/Authorized | open period | Submitted → Approved | ready to post | Sync |
| adjustment post | treasurer/system | Treasurer/System | approved, period open | Approved → Posted | affects expected balance | Sync |
| issue resolve | reviewer/system | Reviewer/System | issue explained/adjusted | Investigating → Adjusted/Explained/Closed | update run | Sync |
| close period | chair/treasurer | Officer | final reconciliation exists, blocking issues cleared | Open/Closing → Closed | generate snapshots, lock period | Sync + async snapshot generation |

**7.8.2 Reconciliation Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| reconciliation_variance_alert_check | Daily | per Chama | alert large variance | retry |
| stale_reconciliation_issue_alert | Daily | per Chama | notify owners/chair of old issues | retry |
| period_close_precheck | Daily / end-period window | per Chama | identify closable periods / blockers | informational |
| statement_snapshot_generation | On close + nightly requeue for failed jobs | per Chama | generate statement artifacts | retry + alert |

**7.9 WORKFLOW MATRIX — NOTIFICATIONS & COMMUNICATION**

**7.9.1 Notification Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| event create | source module action | System | valid event/payload | Event Created | queue build | Async/immediate |
| recipient resolution | event processor | System | template + recipients resolvable | Created → Processed | queue items created | Async |
| queue send | scheduler/worker | System | due time reached | Pending → Sending → Sent/Failed | inbox create for APP | Async |
| read inbox item | user | Member/User | owns inbox item | Unread → Read | timestamp update | Sync |
| retry failed notification | scheduler/admin | System/Admin | retry_count < limit | Failed → Pending | rescheduled send | Async |
| broadcast send | scheduler/admin | System/Admin | scheduled time reached | Draft/Scheduled → Sent | queue per recipient | Async |

**7.9.2 Notification Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| process_notification_queue | Every minute | global/tenant-partitioned | send due queue items | retry |
| retry_failed_notifications | Every 10 min | global | reschedule failed items | capped retries + alert |
| generate_due_reminders | Daily | per Chama | due reminder events | retry |
| generate_meeting_reminders | Hourly | per Chama | meeting reminder events | retry |
| generate_vote_closing_reminders | Hourly | per Chama | reminder events | retry |
| archive_old_inbox_items | Daily | per Chama/global | archive old items | retry |

**7.10 WORKFLOW MATRIX — MEETINGS**

**7.10.1 Meeting Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| schedule meeting | secretary/chair | Officer | valid metadata | Draft → Scheduled | attendee notifications | Sync |
| start meeting | secretary/chair | Officer | scheduled/override valid | Scheduled → In Progress | attendance/minutes open | Sync |
| attendance record | secretary | Secretary | meeting editable | update attendance rows | live quorum recalc | Sync |
| submit minutes | secretary | Secretary | summary present | Draft → Submitted | notify reviewer | Sync |
| publish minutes | chair/authorized | Officer | meeting completed, minutes valid | Submitted → Published | member notification | Sync |
| close meeting | secretary/chair | Officer | attendance + minutes present | Completed → Closed | freeze core records | Sync |
| action item progress | assignee/scheduler | User/System | action item exists | Open → In Progress/Completed/Overdue | alerts | Sync + scheduled |

**7.10.2 Meeting Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| meeting_reminder_queue | Hourly | per Chama | reminders for upcoming meetings | retry |
| overdue_action_item_refresh | Daily | per Chama | mark overdue action items | retry |
| stale_unpublished_minutes_alert | Daily | per Chama | alert secretary/chair | retry |

**7.11 WORKFLOW MATRIX — VOTING & RESOLUTIONS**

**7.11.1 Voting Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| create proposal | secretary/chair | Officer | valid source/context | create Draft | —   | Sync |
| open proposal | secretary/chair/system | Officer/System | eligible voters resolved | Draft → Open | snapshot voters, notify voters | Sync |
| submit vote | eligible voter | Member/User | open, before deadline, no prior vote | create locked vote | update snapshot has_voted | Sync |
| close proposal | scheduler/manual | System/Chair | deadline reached or manual close | Open → Closed | tally | Sync/async |
| tally proposal | system | System | closed proposal | Closed → Approved/Rejected/Invalid | create resolution | Sync |
| enforce resolution | system/authorized | System/Officer | approved resolution, valid linkage | Pending → Applied/Failed | downstream source update | Sync/async |

**7.11.2 Voting Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| proposal_auto_close | Every 15 min / hourly | per Chama | close expired proposals | retry |
| vote_closing_reminder_queue | Hourly | per Chama | remind non-voters | retry |
| stalled_resolution_enforcement_check | Hourly/Daily | per Chama | alert on pending/failed enforcement | retry + alert |

**7.12 WORKFLOW MATRIX — BUDGETING**

**7.12.1 Budget Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| create budget | treasurer | Treasurer | line items valid | create Draft | —   | Sync |
| submit budget | treasurer/secretary | Officer | totals valid | Draft → Pending Approval | create proposal if needed | Sync |
| activate budget | system/treasurer | System/Officer | approved or approval not needed | Pending → Active | budget controls enabled | Sync |
| overrun check | disbursement validate | System | budget line linked | none or escalation/block | notify if overrun | Sync |
| create amendment | treasurer | Treasurer | active budget | create Draft amendment | —   | Sync |
| approve amendment | system/chair | System/Officer | governance passed | Pending → Approved | ready apply | Sync |
| apply amendment | treasurer/system | Treasurer/System | approved amendment | Approved → Applied | version increment | Sync |
| close budget | treasurer/chair | Officer | close criteria met | Active → Closed | lock normal edits | Sync |

**7.12.2 Budget Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| budget_overrun_alert_scan | Daily / near-real-time optional | per Chama | alert unresolved overruns | retry |
| stale_pending_budget_approval_alert | Daily | per Chama | remind approvers | retry |
| budget_period_end_closure_candidates | Daily | per Chama | identify budgets ready to close | informational |

**7.13 WORKFLOW MATRIX — MEMBER LIFECYCLE**

**7.13.1 Member Lifecycle Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| submit application | applicant/admin | User | identity valid | Draft → Submitted/Pending | notify reviewers | Sync |
| approve application | chair/system | Officer/System | rules pass | Pending → Approved → Member Active | create member + role | Sync |
| reject application | chair/system | Officer/System | review complete | → Rejected | notify applicant | Sync |
| change status | chair/admin/system | Officer/System | valid transition | status change | entitlement sync, notifications | Sync |
| assign role | chair/admin | Officer | role rules valid | create role assignment | permission sync | Sync |
| initiate exit | member/admin | User/Officer | allowed | Draft → Submitted/Pending | notify approvers | Sync |
| calculate settlement | treasurer/system | Treasurer/System | exit approved | create Calculated settlement | freeze figures | Sync |
| approve settlement | chair/authorized | Officer | valid calculation | Calculated → Approved | ready for payout | Sync |
| finalize exit | system/admin | System/Officer | payout done or zero-close | Exit In Progress → Exited | close request, statement snapshot | Sync |

**7.13.2 Member Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| dormant_member_scan | Daily/Monthly | per Chama | mark/flag dormant candidates | alert before auto-change if policy |
| pending_application_reminder | Daily | per Chama | remind approvers | retry |
| stale_exit_settlement_alert | Daily | per Chama | alert treasurer/chair | retry |
| member_tenure_snapshot_refresh | Daily | per Chama | refresh derived tenure flags if cached | retry |

**7.14 WORKFLOW MATRIX — INVESTMENT MANAGEMENT**

**7.14.1 Investment Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| create investment proposal | treasurer/secretary | Officer | valid data | Draft | —   | Sync |
| submit proposal | officer | Officer | valid cost/model | Draft → Pending Approval | create governance proposal | Sync |
| approve proposal | system/chair | System/Officer | proposal passed | Pending → Approved | ready for conversion | Sync |
| convert to investment | treasurer/admin | Officer | approved proposal | Approved → Converted / Investment Draft | create investment | Sync |
| activate investment | treasurer/admin | Officer | acquisition + ownership ready | Draft → Active | entitlement baseline | Sync |
| submit valuation | treasurer | Treasurer | valid valuation note | Draft → Submitted | notify approver | Sync |
| approve/apply valuation | chair/system | Officer/System | valuation valid | Submitted → Applied | update current value, entitlements | Sync |
| record return event | treasurer | Treasurer | investment active | create return event | distribution calc maybe | Sync |
| distribute returns | treasurer/system | Treasurer/System | valid return event | Undistributed → Partial/Distributed | create distributions/disbursements | Sync/async |
| close investment | treasurer/admin | Officer | fully realized/closed | Active/Partial → Closed | final analytics update | Sync |

**7.14.2 Investment Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| stale_unvalued_investment_alert | Monthly | per Chama | alert overdue valuations | retry |
| pending_distribution_alert | Daily | per Chama | alert on undistributed returns | retry |
| investment_entitlement_refresh_check | Daily | per Chama | sanity-check entitlements vs latest valuation | retry + integrity alert |

**7.15 WORKFLOW MATRIX — MULTI-CHAMA PLATFORM CONTROLS**

**7.15.1 Platform Control Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| create Chama | platform admin | Platform Admin | unique code/name | new Active Chama | create settings | Sync |
| switch context | user | User | has access | update active context | log switch | Sync |
| archive Chama | platform admin | Platform Admin | no blocking archive conditions | Active/Inactive → Archived | readonly mode | Sync |
| support access override | platform admin | Platform Admin | explicit scope + reason | temporary support context | audit trail | Sync |

**7.15.2 Platform Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| tenant_integrity_scan | Daily | global | detect records missing chama / broken scoping | critical alert |
| stale_context_cleanup | Daily | global | clear invalid session context refs | retry |
| archived_tenant_health_check | Weekly | global | ensure archived tenants readonly integrity | alert only |
| cross-tenant access audit review rollup | Daily | global | summarize support/admin access events | alert if anomalies |

**7.16 WORKFLOW MATRIX — ANALYTICS & REPORTING**

**7.16.1 Analytics Workflow Matrix**

| **Workflow** | **Trigger** | **Actor / Owner** | **Pre-Conditions** | **Transition** | **Side Effects** | **Sync/Async** |
| --- | --- | --- | --- | --- | --- | --- |
| load dashboard | user opens dashboard | User/System | authorized | compute/fetch metrics | none | Sync |
| generate report | user action | User/System | access + valid filters | produce rows | export optional | Sync / async if heavy |
| export report | user action | User/System | export allowed | create file/log | export log | Sync/async |
| refresh cached metric | scheduler | System | metric active | snapshot update | freshness metadata | Scheduled |
| threshold alert | scheduler | System | threshold exceeded | create notification event | alerts | Scheduled |

**7.16.2 Analytics Scheduled Jobs**

| **Job Name** | **Frequency** | **Scope** | **Output** | **Failure Policy** |
| --- | --- | --- | --- | --- |
| metric_snapshot_refresh | Hourly/Daily by metric | per Chama | refresh cached KPIs | retry |
| dashboard_cache_warm | Hourly optional | per Chama | precompute heavy dashboards | skip/retry |
| threshold_alert_scan | Hourly/Daily | per Chama | risk alerts | retry |
| export_cleanup_retention | Daily | global/per Chama | remove expired temp files | retry |

**7.17 MASTER SCHEDULER CATALOGUE**

This is the consolidated scheduler register.

| **Job Code** | **Module** | **Frequency** | **Priority** | **Idempotent** | **Critical** |
| --- | --- | --- | --- | --- | --- |
| SCH001 contribution_cycle_generation | Contributions | Daily | High | Yes | Yes |
| SCH002 contribution_due_status_refresh | Contributions | Daily | High | Yes | Yes |
| SCH003 contribution_overdue_refresh | Contributions | Daily | High | Yes | Yes |
| SCH004 contribution_penalty_apply | Contributions | Daily | High | Yes | Yes |
| SCH005 loan_overdue_refresh | Loans | Daily | High | Yes | Yes |
| SCH006 loan_default_check | Loans | Daily | High | Yes | Yes |
| SCH007 notification_queue_process | Notifications | Every minute | Critical | Yes | Yes |
| SCH008 notification_retry | Notifications | Every 10 min | High | Yes | Yes |
| SCH009 meeting_reminder_queue | Meetings | Hourly | Medium | Yes | No  |
| SCH010 proposal_auto_close | Voting | 15 min/Hourly | High | Yes | Yes |
| SCH011 vote_reminder_queue | Voting | Hourly | Medium | Yes | No  |
| SCH012 budget_overrun_alert_scan | Budgeting | Daily | Medium | Yes | No  |
| SCH013 dormant_member_scan | Member Lifecycle | Daily/Monthly | Medium | Yes | No  |
| SCH014 stale_exit_settlement_alert | Member Lifecycle | Daily | High | Yes | No  |
| SCH015 valuation_staleness_scan | Investments | Monthly | Medium | Yes | No  |
| SCH016 metric_snapshot_refresh | Analytics | Hourly/Daily | Medium | Yes | No  |
| SCH017 threshold_alert_scan | Analytics | Hourly/Daily | Medium | Yes | No  |
| SCH018 tenant_integrity_scan | Platform | Daily | Critical | Yes | Yes |
| SCH019 reconciliation_issue_alert | Reconciliation | Daily | High | Yes | No  |
| SCH020 period_close_precheck | Reconciliation | Daily | Medium | Yes | No  |

This list is baseline, not exhaustive.

**7.18 JOB DEPENDENCY RULES**

Some jobs must run before others.

**7.18.1 Example Dependency Chains**

**Contributions**

1.  cycle generation
2.  due status refresh
3.  overdue refresh
4.  penalty apply
5.  reminder queue

**Loans**

1.  repayment posting / schedule updates
2.  overdue refresh
3.  default check
4.  reminder / risk notifications

**Notifications**

1.  source event emitted
2.  queue items created
3.  queue processor sends
4.  retry job handles failures

**Reconciliation / Close**

1.  transactions posted
2.  reconciliation run
3.  issues resolved / adjustments posted
4.  statement snapshots generated
5.  period close

**7.18.2 Rule**

Dependent jobs must either:

- run in guaranteed order
- or validate prerequisite state before acting

No job may assume another job succeeded without checking required state.

**7.19 TIMEZONE AND DATE EXECUTION RULES**

Because Chamas operate in local time, scheduling must be timezone-aware.

**Rules**

- timestamps stored in UTC
- scheduled business jobs interpret date boundaries using Chama timezone where relevant
- reminders based on due_date or meeting_date must respect Chama timezone
- platform/global jobs may run in system time but must convert tenant windows correctly

Example:

- “due tomorrow” must mean tomorrow in the Chama’s timezone, not merely server UTC rollover

**7.20 IDMPOTENCY RULES FOR AUTOMATIONS**

Every scheduled job that can be retried must be safe.

**Required Idempotent Jobs**

- overdue refresh
- default check
- reminder generation
- notification queue creation
- proposal auto-close
- metric snapshot refresh
- entitlement refresh
- archive/cleanup routines

**Example Rule**

A reminder generator must not create duplicate reminders for the same:

- event type
- recipient
- source record
- reminder window

**7.21 RETRY POLICY MATRIX**

| **Automation Type** | **Retry Strategy** | **Max Retries** | **Escalation** |
| --- | --- | --- | --- |
| Notification send | exponential/backoff or configured interval | 3–5 | alert ops/admin |
| Payment-related async mirror | retry cautiously | 3   | manual review |
| Metric snapshot refresh | retry next cycle | 2–3 | log only / admin alert if persistent |
| Proposal auto-close | retry soon | 3   | critical alert if expired proposals remain |
| Statement snapshot generation | retry queue | 3   | block period close completion if essential |
| Integrity scan failures | retry next cycle | 1–2 | critical alert |

**Rule**

Retries must not create duplicate business outcomes.

**7.22 FAILURE HANDLING RULES**

Automation failures must be visible and classifiable.

**Failure Severity Classes**

| **Severity** | **Meaning** | **Examples** |
| --- | --- | --- |
| Critical | threatens financial integrity or tenant safety | tenant_integrity_scan fail, duplicate disbursement risk |
| High | blocks key user flows or governance | proposal not auto-closing, failed settlement finalization |
| Medium | operational degradation | reminders not sent, stale metrics |
| Low | convenience issue | non-critical dashboard cache miss |

**Required Failure Outputs**

- job log entry
- correlation ID
- Chama scope if applicable
- failure reason
- retry count
- escalation event if threshold crossed

**7.23 AUTOMATION AUDIT RULES**

The following automated actions must leave audit traces:

- automatic status changes (due → overdue, active → defaulted, etc.)
- auto-generated obligations
- auto-closed proposals
- automatic application of valuation or metrics snapshots
- automatic notifications and reminders
- automated period close-related artifacts
- any system-triggered enforcement or reversal

Audit records must identify:

- actor = system/job
- job name/code
- target record
- before/after state where relevant
- timestamp

**7.24 AUTOMATION OWNERSHIP RULES**

Every workflow and job must have a clear owner.

| **Type** | **Owner Meaning** |
| --- | --- |
| Business state transition | module owner + authorized user/system |
| Scheduler job | module owner + platform operations |
| Queue worker | notification/platform layer |
| Integrity scan | platform controls |
| Metric refresh | analytics owner |

No “orphan job” should exist with no accountable owner.

**7.25 AUTOMATION SECURITY RULES**

Automations must not bypass security logic incorrectly.

**Rules**

- system jobs may perform state transitions only if explicitly authorized by design
- jobs must stamp proper audit identity (system, scheduler, worker, etc.)
- jobs must still respect Chama scoping
- admin override jobs must not impersonate users silently
- background jobs must not access unrelated tenant data unnecessarily

**7.26 AUTOMATION PERFORMANCE RULES**

**Rules**

- user-facing actions should enqueue heavy follow-up work instead of blocking
- high-frequency jobs should process in small safe batches
- batch jobs should be Chama-partitionable
- long-running jobs should be resumable where possible
- queue backlogs must be observable

Examples:

- notification queue can batch by tenant
- metric snapshots can batch by metric and Chama
- export generation should be async for large reports

**7.27 AUTOMATION OBSERVABILITY RULES**

Every important automation should expose observability fields:

- last run
- last success
- last failure
- failure count
- pending backlog
- next scheduled run
- average runtime (optional but recommended)

This can power an operations dashboard.

**7.28 AUTOMATION HEALTH DASHBOARD (RECOMMENDED)**

A system operations dashboard should show:

**Queue/Jobs**

- pending notification queue
- failed notification queue
- stale proposals open past deadline
- overdue action items not refreshed
- stale metric snapshots
- failed statement generations
- tenant integrity errors

**Indicators**

- red for critical failures
- amber for degraded behavior
- green for healthy

This is especially useful for admins/platform operators.

**7.29 SECTION 7 CANONICAL AUTOMATION INVARIANTS**

These must always be true:

1.  Scheduled jobs must be idempotent.
2.  Time-based business logic must use Chama timezone semantics where relevant.
3.  Critical financial state transitions must never depend on a silent best-effort job without failure visibility.
4.  Retry must not duplicate business effects.
5.  Every automated mutation must be auditable.
6.  Dependent jobs must validate prerequisite state before acting.
7.  Queue backlogs and automation failures must be observable.
8.  No automation may bypass tenant isolation.

## SECTION 9: IMPLEMENTATION PHASING & RELEASE DEPENDENCIES

**9.1 PURPOSE OF THIS SECTION**

This section defines:

- the phased delivery plan
- module dependencies
- release sequencing
- ERPNext reuse vs customization boundaries
- deployment strategy
- data migration strategy
- environment structure
- go-live readiness criteria

This section ensures:

- nothing is built out of order
- core dependencies are respected
- ERPNext is used efficiently (not fought)
- rollout risk is controlled

**9.2 CORE IMPLEMENTATION PRINCIPLES**

1.  **Do not fight ERPNext (Frappe v16)**
2.  **Build around existing doctypes first, extend only where necessary**
3.  **Stabilize financial backbone before governance layers**
4.  **Do not expose UI before underlying integrity is proven**
5.  **Each phase must produce a usable, testable system slice**
6.  **No phase should depend on unbuilt downstream assumptions**
7.  **Data integrity beats feature completeness**

**9.3 ERPNext REUSE STRATEGY (CRITICAL)**

You said it correctly earlier—this must anchor everything.

**Core reuse areas:**

| **Domain** | **ERPNext/Frappe Component** |
| --- | --- |
| Loans | Frappe Lending |
| Accounting concepts | GL/ledger patterns (even if not fully exposed) |
| Users & Roles | Frappe User + Role system |
| Workflow engine | Frappe Workflows |
| Reports | Query + Script Reports |
| Notifications | Email/SMS framework |
| Scheduler | Background jobs |
| Attachments | File system |
| Permissions | Role + User Permissions |

**Custom layer:**

| **Area** | **Custom** |
| --- | --- |
| Chama context | YES |
| Contribution engine | YES |
| Disbursement control layer | YES |
| Governance (meetings/voting) | YES |
| Investment ownership/valuation | YES |
| Multi-Chama isolation | YES |
| Cross-module formulas | YES |
| Analytics layer | YES |

**9.4 PHASE STRUCTURE OVERVIEW**

We will use **progressive vertical slices**, not horizontal layers.

Each phase delivers:

- working workflows
- usable UI/API
- testable outputs

**9.5 PHASE 0 — FOUNDATION (MANDATORY FIRST)**

**Objective**

Establish platform core and tenant isolation.

**Scope**

**A. Multi-Chama Core**

- Chama DocType
- membership link
- context switching
- tenant scoping enforcement

**B. Member Core**

- Chama Member
- roles within Chama
- status lifecycle (basic)

**C. Permissions Layer**

- role mapping per Chama
- basic access control enforcement

**D. Base Settings**

- Chama Settings
- currency
- timezone
- basic policies

**E. Developer Foundation**

- app structure
- naming conventions
- base API pattern
- logging + audit scaffolding

**Deliverable**

- user can log in
- select Chama
- see only their Chama data

**Exit Criteria**

- zero cross-tenant leakage
- roles enforced correctly
- audit logs working

**9.6 PHASE 1 — FINANCIAL BACKBONE (CRITICAL PATH)**

This is the most important phase. Do not rush it.

**Modules**

**A. Contributions (Core Engine)**

- obligation generation
- payment recording
- allocation logic
- overdue detection
- penalties (basic)

**B. Loans (ERPNext Lending Integration)**

- loan application
- guarantor model (custom)
- approval flow
- disbursement integration
- repayment tracking

**C. Disbursements (Core)**

- request → approval → execution
- integration with loans + general payouts
- budget placeholder (no enforcement yet)

**D. Basic Reconciliation (Lite)**

- expected balance computation
- manual actual entry
- variance calculation (no deep issue handling yet)

**Deliverable**

You can:

- collect money
- lend money
- disburse money
- track balances

**Exit Criteria**

- no duplicate financial entries
- allocation logic correct
- loan balances match Lending
- reconciliation math correct

**9.7 PHASE 2 — GOVERNANCE LAYER**

**Modules**

**A. Meetings**

- scheduling
- attendance
- minutes

**B. Voting**

- proposals
- voting
- tally logic

**C. Notifications (Basic)**

- event-based notifications
- inbox
- reminders

**Deliverable**

- decisions can be made formally
- actions can be approved properly

**Exit Criteria**

- quorum logic correct
- voting immutable
- meeting records consistent

**9.8 PHASE 3 — CONTROL & STRUCTURE**

**Modules**

**A. Budgeting**

- budgets
- line items
- enforcement on disbursements

**B. Reconciliation (Full)**

- issue tracking
- adjustments
- closing periods
- statement snapshots

**C. Member Lifecycle**

- onboarding
- role management
- exit + settlement

**Deliverable**

- system is governable and auditable
- financial statements reliable

**Exit Criteria**

- reconciliation closes correctly
- settlement calculations accurate
- budget enforcement working

**9.9 PHASE 4 — INVESTMENT LAYER**

**Modules**

**A. Investment Management**

- ownership structures
- valuation model
- entitlement calculation

**B. Return Distribution**

- distribution events
- disbursement linkage

**Deliverable**

- group investments fully tracked
- ownership transparent

**Exit Criteria**

- entitlement matches valuation
- distributions correct per ownership snapshot

**9.10 PHASE 5 — ANALYTICS & OPTIMIZATION**

**Modules**

**A. Dashboards**

- member
- treasurer
- chair

**B. Reports**

- full catalogue

**C. Metric Engine**

- cached metrics
- trend analysis

**Deliverable**

- decision-support system operational

**Exit Criteria**

- dashboards match reports
- metrics match formulas
- performance acceptable

**9.11 PHASE 6 — HARDENING & SCALE**

**Scope**

**A. Performance Optimization**

- caching
- query optimization
- async jobs

**B. Security Hardening**

- audit completeness
- permission audits
- penetration checks

**C. Mobile Optimization**

- API refinement
- payload tuning

**D. Operational Tools**

- health dashboard
- job monitoring

**Deliverable**

- production-ready system

**9.12 DEPENDENCY MATRIX (CRITICAL)**

**9.12.1 Hard Dependencies**

| **Module** | **Depends On** |
| --- | --- |
| Contributions | Member, Chama |
| Loans | Member, Contributions (eligibility), Lending |
| Disbursements | Loans, Contributions |
| Reconciliation | Contributions, Loans, Disbursements |
| Budgeting | Disbursements |
| Voting | Member |
| Meetings | Member |
| Member Lifecycle | All financial modules |
| Investment | Member, Disbursement |
| Analytics | All modules |

**9.12.2 Dependency Rule**

A module cannot be exposed to users until:

- all its upstream dependencies are stable
- its outputs match Section 5 formulas
- it passes integration tests with dependent modules

**9.13 DATA MIGRATION STRATEGY**

If migrating from existing systems:

**Steps**

1.  import Chamas
2.  import Members
3.  import Contributions history
4.  import Loans (into Lending-compatible structure)
5.  import Disbursement history
6.  import Investment data
7.  reconstruct balances
8.  run reconciliation baseline

**Rule**

Post-migration:

- system must produce same totals as legacy system
- discrepancies must be reconciled before go-live

**9.14 ENVIRONMENT STRATEGY**

| **Environment** | **Purpose** |
| --- | --- |
| Dev | active development |
| Staging | integration + UAT |
| Production | live |

**Rules**

- no direct development in production
- migrations tested in staging first
- seed/demo data isolated from real data

**9.15 RELEASE STRATEGY**

**9.15.1 Internal Release (Alpha)**

- core flows tested
- not exposed to real users

**9.15.2 Controlled Pilot (Beta)**

- limited Chamas
- monitored usage
- feedback loop

**9.15.3 General Release**

- all modules stable
- documentation ready
- support processes in place

**9.16 GO-LIVE READINESS CHECKLIST**

System must satisfy:

**Financial Integrity**

- balances match expectations
- reconciliation works
- no duplicate transaction paths

**Security**

- tenant isolation verified
- roles enforced
- no data leakage

**Workflows**

- all critical workflows complete
- no dead-end states

**Reporting**

- reports match modules
- statements accurate

**Automation**

- jobs running
- no critical failures

**9.17 RISKS AND MITIGATION**

**Risk 1 — Fighting ERPNext**

**Mitigation:** reuse first, extend second

**Risk 2 — Inconsistent Calculations**

**Mitigation:** enforce Section 5 strictly

**Risk 3 — Premature UI Exposure**

**Mitigation:** backend-first validation

**Risk 4 — Cross-Module Drift**

**Mitigation:** integration testing per phase

**Risk 5 — Overengineering Early**

**Mitigation:** phase discipline

**9.18 SECTION 9 INVARIANTS**

1.  No module is built in isolation from dependencies.
2.  Financial backbone must stabilize before governance layers.
3.  ERPNext must be leveraged, not replaced.
4.  Each phase must produce a working system slice.
5.  Migration must preserve financial truth.
6.  Go-live must only occur after reconciliation correctness.

**SECTION 9: IMPLEMENTATION PHASING & RELEASE DEPENDENCIES**

**9.1 PURPOSE OF THIS SECTION**

This section defines:

- the phased delivery plan
- module dependencies
- release sequencing
- ERPNext reuse vs customization boundaries
- deployment strategy
- data migration strategy
- environment structure
- go-live readiness criteria

This section ensures:

- nothing is built out of order
- core dependencies are respected
- ERPNext is used efficiently (not fought)
- rollout risk is controlled

**9.2 CORE IMPLEMENTATION PRINCIPLES**

1.  **Do not fight ERPNext (Frappe v16)**
2.  **Build around existing doctypes first, extend only where necessary**
3.  **Stabilize financial backbone before governance layers**
4.  **Do not expose UI before underlying integrity is proven**
5.  **Each phase must produce a usable, testable system slice**
6.  **No phase should depend on unbuilt downstream assumptions**
7.  **Data integrity beats feature completeness**

**9.3 ERPNext REUSE STRATEGY (CRITICAL)**

You said it correctly earlier—this must anchor everything.

**Core reuse areas:**

| **Domain** | **ERPNext/Frappe Component** |
| --- | --- |
| Loans | Frappe Lending |
| Accounting concepts | GL/ledger patterns (even if not fully exposed) |
| Users & Roles | Frappe User + Role system |
| Workflow engine | Frappe Workflows |
| Reports | Query + Script Reports |
| Notifications | Email/SMS framework |
| Scheduler | Background jobs |
| Attachments | File system |
| Permissions | Role + User Permissions |

**Custom layer:**

| **Area** | **Custom** |
| --- | --- |
| Chama context | YES |
| Contribution engine | YES |
| Disbursement control layer | YES |
| Governance (meetings/voting) | YES |
| Investment ownership/valuation | YES |
| Multi-Chama isolation | YES |
| Cross-module formulas | YES |
| Analytics layer | YES |

**9.4 PHASE STRUCTURE OVERVIEW**

We will use **progressive vertical slices**, not horizontal layers.

Each phase delivers:

- working workflows
- usable UI/API
- testable outputs

**9.5 PHASE 0 — FOUNDATION (MANDATORY FIRST)**

**Objective**

Establish platform core and tenant isolation.

**Scope**

**A. Multi-Chama Core**

- Chama DocType
- membership link
- context switching
- tenant scoping enforcement

**B. Member Core**

- Chama Member
- roles within Chama
- status lifecycle (basic)

**C. Permissions Layer**

- role mapping per Chama
- basic access control enforcement

**D. Base Settings**

- Chama Settings
- currency
- timezone
- basic policies

**E. Developer Foundation**

- app structure
- naming conventions
- base API pattern
- logging + audit scaffolding

**Deliverable**

- user can log in
- select Chama
- see only their Chama data

**Exit Criteria**

- zero cross-tenant leakage
- roles enforced correctly
- audit logs working

**9.6 PHASE 1 — FINANCIAL BACKBONE (CRITICAL PATH)**

This is the most important phase. Do not rush it.

**Modules**

**A. Contributions (Core Engine)**

- obligation generation
- payment recording
- allocation logic
- overdue detection
- penalties (basic)

**B. Loans (ERPNext Lending Integration)**

- loan application
- guarantor model (custom)
- approval flow
- disbursement integration
- repayment tracking

**C. Disbursements (Core)**

- request → approval → execution
- integration with loans + general payouts
- budget placeholder (no enforcement yet)

**D. Basic Reconciliation (Lite)**

- expected balance computation
- manual actual entry
- variance calculation (no deep issue handling yet)

**Deliverable**

You can:

- collect money
- lend money
- disburse money
- track balances

**Exit Criteria**

- no duplicate financial entries
- allocation logic correct
- loan balances match Lending
- reconciliation math correct

**9.7 PHASE 2 — GOVERNANCE LAYER**

**Modules**

**A. Meetings**

- scheduling
- attendance
- minutes

**B. Voting**

- proposals
- voting
- tally logic

**C. Notifications (Basic)**

- event-based notifications
- inbox
- reminders

**Deliverable**

- decisions can be made formally
- actions can be approved properly

**Exit Criteria**

- quorum logic correct
- voting immutable
- meeting records consistent

**9.8 PHASE 3 — CONTROL & STRUCTURE**

**Modules**

**A. Budgeting**

- budgets
- line items
- enforcement on disbursements

**B. Reconciliation (Full)**

- issue tracking
- adjustments
- closing periods
- statement snapshots

**C. Member Lifecycle**

- onboarding
- role management
- exit + settlement

**Deliverable**

- system is governable and auditable
- financial statements reliable

**Exit Criteria**

- reconciliation closes correctly
- settlement calculations accurate
- budget enforcement working

**9.9 PHASE 4 — INVESTMENT LAYER**

**Modules**

**A. Investment Management**

- ownership structures
- valuation model
- entitlement calculation

**B. Return Distribution**

- distribution events
- disbursement linkage

**Deliverable**

- group investments fully tracked
- ownership transparent

**Exit Criteria**

- entitlement matches valuation
- distributions correct per ownership snapshot

**9.10 PHASE 5 — ANALYTICS & OPTIMIZATION**

**Modules**

**A. Dashboards**

- member
- treasurer
- chair

**B. Reports**

- full catalogue

**C. Metric Engine**

- cached metrics
- trend analysis

**Deliverable**

- decision-support system operational

**Exit Criteria**

- dashboards match reports
- metrics match formulas
- performance acceptable

**9.11 PHASE 6 — HARDENING & SCALE**

**Scope**

**A. Performance Optimization**

- caching
- query optimization
- async jobs

**B. Security Hardening**

- audit completeness
- permission audits
- penetration checks

**C. Mobile Optimization**

- API refinement
- payload tuning

**D. Operational Tools**

- health dashboard
- job monitoring

**Deliverable**

- production-ready system

**9.12 DEPENDENCY MATRIX (CRITICAL)**

**9.12.1 Hard Dependencies**

| **Module** | **Depends On** |
| --- | --- |
| Contributions | Member, Chama |
| Loans | Member, Contributions (eligibility), Lending |
| Disbursements | Loans, Contributions |
| Reconciliation | Contributions, Loans, Disbursements |
| Budgeting | Disbursements |
| Voting | Member |
| Meetings | Member |
| Member Lifecycle | All financial modules |
| Investment | Member, Disbursement |
| Analytics | All modules |

**9.12.2 Dependency Rule**

A module cannot be exposed to users until:

- all its upstream dependencies are stable
- its outputs match Section 5 formulas
- it passes integration tests with dependent modules

**9.13 DATA MIGRATION STRATEGY**

If migrating from existing systems:

**Steps**

1.  import Chamas
2.  import Members
3.  import Contributions history
4.  import Loans (into Lending-compatible structure)
5.  import Disbursement history
6.  import Investment data
7.  reconstruct balances
8.  run reconciliation baseline

**Rule**

Post-migration:

- system must produce same totals as legacy system
- discrepancies must be reconciled before go-live

**9.14 ENVIRONMENT STRATEGY**

| **Environment** | **Purpose** |
| --- | --- |
| Dev | active development |
| Staging | integration + UAT |
| Production | live |

**Rules**

- no direct development in production
- migrations tested in staging first
- seed/demo data isolated from real data

**9.15 RELEASE STRATEGY**

**9.15.1 Internal Release (Alpha)**

- core flows tested
- not exposed to real users

**9.15.2 Controlled Pilot (Beta)**

- limited Chamas
- monitored usage
- feedback loop

**9.15.3 General Release**

- all modules stable
- documentation ready
- support processes in place

**9.16 GO-LIVE READINESS CHECKLIST**

System must satisfy:

**Financial Integrity**

- balances match expectations
- reconciliation works
- no duplicate transaction paths

**Security**

- tenant isolation verified
- roles enforced
- no data leakage

**Workflows**

- all critical workflows complete
- no dead-end states

**Reporting**

- reports match modules
- statements accurate

**Automation**

- jobs running
- no critical failures

**9.17 RISKS AND MITIGATION**

**Risk 1 — Fighting ERPNext**

**Mitigation:** reuse first, extend second

**Risk 2 — Inconsistent Calculations**

**Mitigation:** enforce Section 5 strictly

**Risk 3 — Premature UI Exposure**

**Mitigation:** backend-first validation

**Risk 4 — Cross-Module Drift**

**Mitigation:** integration testing per phase

**Risk 5 — Overengineering Early**

**Mitigation:** phase discipline

**9.18 SECTION 9 INVARIANTS**

1.  No module is built in isolation from dependencies.
2.  Financial backbone must stabilize before governance layers.
3.  ERPNext must be leveraged, not replaced.
4.  Each phase must produce a working system slice.
5.  Migration must preserve financial truth.
6.  Go-live must only occur after reconciliation correctness.

## SECTION 10: ACCEPTANCE CRITERIA & UAT BASELINE

**10.1 PURPOSE OF THIS SECTION**

This section defines:

- what must be tested
- how it must be tested
- what “pass” means
- what “fail” means
- mandatory scenarios per module
- cross-module validation scenarios
- financial integrity validation
- audit and security validation

This is the **contract between product, engineering, and operations**.

**10.2 UAT PRINCIPLES**

1.  **Test real workflows, not isolated fields**
2.  **Validate outputs against Section 5 formulas**
3.  **Test cross-module consistency**
4.  **Test failure paths, not just success paths**
5.  **Test role-based access rigorously**
6.  **Test edge cases explicitly**
7.  **No “it looks right”—everything must reconcile**
8.  **Test data must be auditable and reproducible**

**10.3 UAT STRUCTURE**

Each test case must include:

| **Field** | **Description** |
| --- | --- |
| Test ID | unique identifier |
| Module | module under test |
| Scenario | description |
| Pre-Conditions | setup required |
| Steps | actions performed |
| Expected Result | exact expected outcome |
| Validation Method | how result is verified |
| Pass/Fail | result |
| Notes | issues/observations |

**10.4 GLOBAL ACCEPTANCE CRITERIA**

The system is acceptable only if ALL are true:

**Financial Integrity**

- balances reconcile exactly
- no duplicate transactions
- no orphan records

**Security**

- no cross-Chama data leakage
- permissions enforced correctly

**Workflows**

- no invalid state transitions
- all workflows complete end-to-end

**Reporting**

- reports = dashboards = source data

**Automation**

- jobs run without critical failures
- no duplicate effects

**10.5 MODULE UAT — CONTRIBUTIONS**

**Test Case CN-001 — Obligation Generation**

**Scenario:** Generate contribution cycle

**Expected:**

- obligations created for all eligible members
- correct amounts per category
- due dates correct

**Validation:**

- count obligations = eligible members
- amounts match configuration

**Test Case CN-002 — Payment Allocation**

**Scenario:** Member pays partial + multiple obligations

**Expected:**

- oldest-first allocation
- correct outstanding values
- no negative balances

**Test Case CN-003 — Overdue Transition**

**Scenario:** Due passes grace period

**Expected:**

- status → Overdue
- overdue_days computed correctly

**Test Case CN-004 — Penalty Application**

**Scenario:** Overdue obligation with penalty rule

**Expected:**

- penalty obligation created
- linked to original obligation

**Test Case CN-005 — Reversal**

**Scenario:** Reverse payment

**Expected:**

- allocation reversed
- outstanding recalculated
- audit log created

**10.6 MODULE UAT — LOANS**

**Test Case LN-001 — Eligibility Enforcement**

**Scenario:** Member applies exceeding eligibility

**Expected:**

- request rejected
- correct error code returned

**Test Case LN-002 — Guarantor Sufficiency**

**Scenario:** insufficient guarantor coverage

**Expected:**

- cannot submit/approve

**Test Case LN-003 — Approval Workflow**

**Expected:**

- status transitions correct
- notifications triggered

**Test Case LN-004 — Disbursement Sync**

**Expected:**

- loan marked disbursed
- reflected in disbursement + reconciliation

**Test Case LN-005 — Overdue Detection**

**Expected:**

- status → Overdue after missed payment

**Test Case LN-006 — Default Transition**

**Expected:**

- default triggered after threshold

**10.7 MODULE UAT — DISBURSEMENTS**

**Test Case DB-001 — Approval Flow**

**Expected:**

- escalation works
- approvals enforced

**Test Case DB-002 — Execution**

**Expected:**

- executed amount recorded
- reconciliation updated
- budget updated

**Test Case DB-003 — Failure Handling**

**Expected:**

- failed state recorded
- no financial duplication

**Test Case DB-004 — Reversal**

**Expected:**

- compensating entry created
- audit trail present

**10.8 MODULE UAT — RECONCILIATION**

**Test Case RC-001 — Expected Balance**

**Expected:**

- computed from transactions exactly

**Test Case RC-002 — Variance Detection**

**Expected:**

- variance = actual - expected

**Test Case RC-003 — Adjustment Posting**

**Expected:**

- affects expected balance
- audit logged

**Test Case RC-004 — Period Close**

**Expected:**

- snapshot generated
- no further edits allowed

**10.9 MODULE UAT — GOVERNANCE**

**Test Case GV-001 — Quorum**

**Expected:**

- quorum computed correctly

**Test Case GV-002 — Voting Lock**

**Expected:**

- vote cannot be changed after submission

**Test Case GV-003 — Tally**

**Expected:**

- result matches rules (simple/absolute/weighted)

**Test Case GV-004 — Enforcement**

**Expected:**

- source object updated

**10.10 MODULE UAT — BUDGETING**

**Test Case BG-001 — Budget Creation**

**Expected:**

- totals correct

**Test Case BG-002 — Overrun Detection**

**Expected:**

- block or escalate correctly

**Test Case BG-003 — Amendment**

**Expected:**

- versioning maintained

**10.11 MODULE UAT — MEMBER LIFECYCLE**

**Test Case MB-001 — Status Transition**

**Expected:**

- valid transitions only

**Test Case MB-002 — Exit Settlement**

**Expected:**

- payout = formula (Section 5)
- no mismatch with reports

**Test Case MB-003 — Role Assignment**

**Expected:**

- permissions update immediately

**10.12 MODULE UAT — INVESTMENTS**

**Test Case IV-001 — Ownership Calculation**

**Expected:**

- ownership % correct

**Test Case IV-002 — Valuation Application**

**Expected:**

- current valuation updated
- entitlements updated

**Test Case IV-003 — Distribution**

**Expected:**

- payouts proportional to ownership snapshot

**10.13 MODULE UAT — ANALYTICS**

**Test Case AN-001 — Metric Consistency**

**Expected:**

- dashboard = report

**Test Case AN-002 — Drilldown**

**Expected:**

- matches source data

**Test Case AN-003 — Export**

**Expected:**

- matches report exactly

**10.14 CROSS-MODULE UAT (CRITICAL)**

**Test Case XM-001 — End-to-End Financial Flow**

**Scenario:**

- contribution → loan → repayment → disbursement → reconciliation

**Expected:**

- all balances consistent
- reconciliation variance = 0

**Test Case XM-002 — Member Exit**

**Scenario:**

- member exits with loans + contributions + investments

**Expected:**

- settlement matches all modules

**Test Case XM-003 — Budget Enforcement**

**Scenario:**

- disbursement exceeds budget

**Expected:**

- blocked or escalated

**Test Case XM-004 — Governance Enforcement**

**Scenario:**

- proposal approved → disbursement

**Expected:**

- disbursement reflects decision

**Test Case XM-005 — Multi-Chama Isolation**

**Scenario:**

- user belongs to multiple Chamas

**Expected:**

- no data leakage

**10.15 SECURITY UAT**

**Test Case SEC-001 — Unauthorized Access**

**Expected:**

- blocked

**Test Case SEC-002 — Cross-Tenant Access**

**Expected:**

- rejected

**Test Case SEC-003 — Role Enforcement**

**Expected:**

- actions limited by role

**Test Case SEC-004 — API Abuse**

**Expected:**

- rate limits enforced

**10.16 AUTOMATION UAT**

**Test Case AU-001 — Scheduler Runs**

**Expected:**

- jobs execute

**Test Case AU-002 — Idempotency**

**Expected:**

- no duplicate effects

**Test Case AU-003 — Failure Handling**

**Expected:**

- retry + alert

**10.17 PERFORMANCE UAT**

**Test Case PF-001 — Dashboard Load**

**Expected:**

- acceptable response time

**Test Case PF-002 — Report Generation**

**Expected:**

- large reports handled

**Test Case PF-003 — Concurrent Actions**

**Expected:**

- no race conditions

**10.18 ACCEPTANCE SIGN-OFF CRITERIA**

System is accepted only if:

- ALL critical test cases pass
- NO financial inconsistencies exist
- NO security violations found
- NO critical automation failures
- reconciliation validated end-to-end
- reports verified against source data

**10.19 REJECTION CONDITIONS**

System must NOT go live if:

- balances do not reconcile
- duplicate transactions possible
- cross-Chama leakage exists
- workflows break in edge cases
- reports mismatch modules

**10.20 SECTION 10 INVARIANTS**

1.  Every feature must be testable.
2.  Every test must have a deterministic expected result.
3.  Financial correctness is non-negotiable.
4.  Cross-module consistency must be proven.
5.  Security must be validated, not assumed.

# SECTION 5: CURSOR DEVELOPMENT & CODE GENERATION RULES

**11.1 PURPOSE**

This document defines **strict rules for using Cursor** to build the system.

It ensures:

- consistent code structure
- correct financial logic implementation
- tenant safety
- alignment with PRD Sections 1–10
- controlled AI-assisted development

This document is **binding for all generated code**.

**11.2 CORE PRINCIPLES**

1.  Cursor is an **assistant**, not an architect
2.  All architecture decisions come from the PRD
3.  Every piece of generated code must be reviewed
4.  No business logic may contradict Section 5
5.  No shortcuts on tenant isolation
6.  Code must be **predictable, testable, and traceable**

**11.3 PROMPTING RULES (CRITICAL)**

**11.3.1 One Task Per Prompt**

Each Cursor prompt must:

- implement ONE artifact only
- be scoped tightly

**✅ GOOD**

- “Create DocType Chama Member”
- “Implement allocation service for contributions”

**❌ BAD**

- “Build contributions module”
- “Implement full system”

**11.3.2 Prompt Structure**

Every prompt must include:

- context (ERPNext v16, Chama system)
- exact artifact type
- required fields or behavior
- validation rules
- reference to PRD logic where relevant

**11.3.3 No Ambiguity Rule**

Prompts must NOT:

- leave field meanings undefined
- allow Cursor to invent business rules
- skip validation requirements

**11.3.4 Iterative Refinement**

Workflow:

1.  Generate code
2.  Review manually
3.  Fix issues
4.  Test
5.  Move forward

Never chain prompts blindly.

**11.4 CODE STRUCTURE RULES**

**11.4.1 Separation of Concerns**

| **Layer** | **Responsibility** |
| --- | --- |
| DocType | schema + minimal validation |
| Service Layer | business logic |
| API Layer | input/output + orchestration |
| Scheduler | time-based execution |
| Reports | read-only aggregation |

**11.4.2 Strict Rule**

- ❌ No financial logic inside DocType UI methods
- ❌ No business logic inside JS
- ❌ No cross-module logic duplication

**11.4.3 Folder Structure (MANDATORY)**

chama_app/  
chama_core/  
chama_contributions/  
chama_loans/  
chama_disbursements/  
chama_reconciliation/  
chama_notifications/  
chama_reports/

**11.5 FINANCIAL LOGIC RULES (NON-NEGOTIABLE)**

**11.5.1 Source of Truth**

All formulas must match:  
👉 Section 5 — Canonical Formulas

**11.5.2 Centralized Logic**

Must exist as services:

- allocation_engine.py
- reconciliation_engine.py
- loan_eligibility_engine.py
- settlement_engine.py

**11.5.3 Forbidden Patterns**

❌ Inline calculations in:

- API handlers
- DocType controllers
- reports

❌ Recomputing formulas differently in different modules

**11.5.4 Required Pattern**

result = allocation_engine.allocate(payment)

**11.6 TENANT SAFETY RULES (CRITICAL)**

**11.6.1 Mandatory Filter**

Every query must include:

filters={"chama": active_chama}

**11.6.2 Validation**

Every API must:

- verify active Chama
- verify record belongs to that Chama

**11.6.3 Forbidden**

❌ Queries without Chama filter  
❌ Cross-Chama joins  
❌ Implicit tenant assumptions

**11.7 API RULES**

**11.7.1 Standard Response**

Must use:

- success_response()
- error_response()

**11.7.2 Mandatory Validation Order**

1.  authentication
2.  chama context
3.  permissions
4.  input validation
5.  state validation

**11.7.3 No Direct DB Writes**

APIs must:

- call services
- not manipulate DB directly

**11.8 WORKFLOW RULES**

**11.8.1 Status Control**

Statuses must:

- match PRD exactly
- not be invented dynamically

**11.8.2 Transitions**

Every transition must:

- be explicit
- be validated

**11.8.3 Forbidden**

❌ setting status arbitrarily  
❌ skipping workflow states

**11.9 NAMING RULES**

Must match Section 8.

Examples:

- amount_due
- outstanding_balance
- approved_amount

**Forbidden**

❌ amt_due  
❌ balance2  
❌ temp_value

**11.10 ERROR HANDLING RULES**

**11.10.1 No Silent Failures**

❌ try/except pass  
❌ swallowing exceptions

**11.10.2 Required**

frappe.throw("Clear message", frappe.ValidationError)

**11.11 AUDIT RULES**

Every financial action must:

- log actor
- log timestamp
- log before/after state if applicable

**Forbidden**

❌ silent updates  
❌ overwrite without trace

**11.12 TESTING RULES**

**11.12.1 Every Service Must Be Testable**

Cursor-generated code must:

- accept inputs clearly
- return outputs clearly

**11.12.2 Manual Testing Required**

After each task:

- create test data
- validate results
- verify against formulas

**11.13 PERFORMANCE RULES**

**11.13.1 No Heavy Logic in APIs**

Heavy operations must:

- be async
- or optimized

**11.13.2 Batch Operations**

Use batching for:

- notifications
- metrics
- updates

**11.14 ANTI-PATTERNS (STRICTLY FORBIDDEN)**

**❌ Architecture Violations**

- mixing logic across layers
- embedding services inside DocTypes

**❌ Financial Violations**

- duplicate formulas
- inconsistent calculations

**❌ Security Violations**

- missing chama filter
- bypassing permission checks

**❌ Cursor Misuse**

- generating multiple modules at once
- accepting code blindly

**11.15 CURSOR USAGE DISCIPLINE**

**11.15.1 Golden Workflow**

1.  Select ONE task
2.  Generate code
3.  Review manually
4.  Fix issues
5.  Test
6.  Commit
7.  Move forward

**11.15.2 Hard Rules**

- Never generate >1 task at a time
- Never skip testing
- Never trust generated code blindly
- Always compare against PRD

**11.16 REVIEW CHECKLIST (MANDATORY BEFORE ACCEPTING CODE)**

Before accepting Cursor output:

- matches PRD
- fields correctly named
- chama enforced
- no duplicate logic
- validation present
- no silent failures
- readable code
- testable

**11.17 FINAL INVARIANTS**

These must ALWAYS hold:

1.  Every record is tenant-scoped
2.  Every financial number matches Section 5
3.  Every API enforces authorization
4.  Every workflow is controlled
5.  Every automation is idempotent
6.  Every report matches source data
7.  Every piece of code is explainable

# SECTION 6: FRAPPE ECOSYSTEM REUSE POLICY

**12.1 PURPOSE**

This document defines:

- how the system uses **ERPNext / Frappe v16**
- how and when to use **Frappe ecosystem apps**
- what must **never be reimplemented**
- how custom modules must integrate with ecosystem modules

This document is **binding for all development and Cursor-generated code**.

**12.2 CORE PRINCIPLE**

**Reuse first. Extend second. Never replace without justification.**

**12.3 SYSTEM ARCHITECTURE POSITIONING**

The system consists of three layers:

**1\. PLATFORM LAYER (Frappe / ERPNext)**

This provides:

- Users
- Roles
- Permissions
- Workflows
- Scheduler
- Reports
- API framework
- File storage
- Background jobs

👉 This layer is **never reimplemented**

**2\. ECOSYSTEM LAYER (Frappe Apps)**

Includes:

- **Frappe Lending**
- **Frappe HRMS**
- Any other official Frappe apps

👉 These are reused where they are **authoritative**

**3\. CHAMA APPLICATION LAYER (CUSTOM)**

Your system:

- chama_core
- chama_contributions
- chama_loans (wrapper)
- chama_disbursements
- chama_reconciliation
- chama_governance
- chama_investments

👉 This layer implements:

- Chama-specific behavior
- Multi-tenant isolation
- Cross-module orchestration

**12.4 MANDATORY REUSE RULES**

**12.4.1 Loans MUST use Frappe Lending**

**Rule:**

All loan lifecycle logic must be handled by:  
👉 **Frappe Lending**

**This includes:**

- loan accounts
- disbursement logic
- repayment schedules
- interest calculations
- loan status transitions
- amortization

**Chama layer responsibilities (allowed):**

- attach chama field
- attach member mapping
- enforce Chama eligibility rules
- enforce guarantor rules
- add approval overlays
- integrate with notifications
- expose APIs
- reporting

**Forbidden:**

❌ Rebuilding loan engine  
❌ Custom amortization logic  
❌ Custom repayment schedule system  
❌ Duplicating loan balances outside Lending

**12.4.2 ERPNext Core Features MUST NOT be duplicated**

**Must reuse:**

| **Feature** | **Source** |
| --- | --- |
| Users | Frappe User |
| Roles | Frappe Role |
| Permissions | Frappe Permission system |
| Workflows | Frappe Workflow |
| Scheduler | Background jobs |
| Notifications | Email/SMS framework |

**Forbidden:**

❌ Custom user system  
❌ Custom role engine  
❌ Custom workflow engine  
❌ Custom scheduler framework

**12.4.3 HRMS is OPTIONAL**

Use **Frappe HRMS** only if:

- you introduce operational staff
- payroll is needed
- employee lifecycle becomes complex

**For v1:**

👉 DO NOT integrate HRMS

**12.5 INTEGRATION PATTERN RULES**

**12.5.1 Extension, Not Modification**

**Allowed:**

- Custom fields
- Event hooks
- Wrapper services
- Integration APIs

**Forbidden:**

❌ Editing core app files  
❌ Forking Frappe apps  
❌ Changing core logic

**12.5.2 Wrapper Pattern (MANDATORY)**

Example for Loans:

chama_loans/  
services/  
loan_service.py # wraps Lending

**Example behavior:**

def apply_loan(member, chama, amount):  
validate_chama_eligibility(member, chama)  
return lending_create_loan(...)

**12.5.3 Event Hook Pattern**

Use Frappe hooks:

- on_submit
- on_update
- after_insert

Example:

- when loan disbursed → trigger Chama notification
- when repayment posted → update analytics

**12.5.4 Data Ownership Rule**

| **Domain** | **Source of Truth** |
| --- | --- |
| Loans | Lending |
| Contributions | Chama |
| Members | Chama |
| Users | Frappe |
| Roles | Frappe |
| Disbursements | Chama |

**12.6 DATA SYNCHRONIZATION RULES**

**12.6.1 No Duplicate Truth**

Example:

- loan balance must only exist in Lending
- Chama must read, not recompute

**12.6.2 Read vs Write Rules**

| **Action** | **Rule** |
| --- | --- |
| Read loan data | from Lending |
| Write loan data | via Lending APIs |
| Extend loan | via custom fields |

**12.6.3 Sync Events**

Must be triggered on:

- loan disbursement
- repayment posting
- loan closure

**12.7 CURSOR-SPECIFIC RULES**

**12.7.1 Cursor must not invent replacements**

Forbidden prompts:

❌ “Build a loan system”  
❌ “Create amortization logic”

**12.7.2 Required prompt pattern**

Example:

Extend Frappe Lending Loan DocType with Chama-specific fields and validation.

**12.7.3 Enforcement**

Every Cursor-generated loan-related code must be reviewed for:

- duplication of Lending logic
- violation of reuse rules

**12.8 EXTENSION POINTS (ALLOWED CUSTOMIZATION)**

**Loans**

- guarantors (custom DocType)
- Chama eligibility logic
- approval workflows
- reporting
- notifications

**Contributions**

Fully custom:

- obligations
- allocation engine
- penalties

**Disbursements**

Fully custom:

- approval layer
- execution tracking

**Governance**

Fully custom

**Investments**

Fully custom

**12.9 ANTI-PATTERNS (STRICTLY FORBIDDEN)**

**❌ Rebuilding Lending features**

**❌ Copying ERPNext core logic into custom app**

**❌ Creating parallel systems (e.g., duplicate loan tables)**

**❌ Mixing core and custom responsibilities**

**❌ Bypassing ecosystem APIs**

**12.10 VERSION ALIGNMENT RULE**

System must align with:

- ERPNext v16
- Frappe v16
- Compatible versions of Lending

**Forbidden:**

❌ mixing incompatible versions  
❌ modifying ecosystem internals to “make it work”

**12.11 FUTURE EXTENSIBILITY**

Allowed future integrations:

- Payment gateways
- Banking APIs
- SMS providers
- Credit scoring services

Must follow same rule:  
👉 integrate, do not replace core systems

**12.12 REVIEW CHECKLIST**

Before accepting any module:

- Are we reusing ecosystem correctly?
- Are we duplicating any Lending logic?
- Are we modifying core app files?
- Are we introducing parallel systems?
- Is data ownership respected?

**12.13 FINAL INVARIANTS**

1.  Lending is the single source of truth for loans
2.  ERPNext core features are never duplicated
3.  Custom app extends, never replaces
4.  No forked ecosystem apps
5.  All integrations use clean extension patterns