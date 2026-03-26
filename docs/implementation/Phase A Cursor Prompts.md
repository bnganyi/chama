**Phase A — Cursor Prompts**

**A-001 — Create Chama DocType**

Create a custom Frappe/ERPNext v16 DocType named "Chama" for a multi-tenant Chama platform.  
<br/>Requirements:  
\- Module: Chama Core  
\- Is Submittable: No  
\- Naming: autoname with format CH-.####  
\- Add these fields:  
1\. chama_name (Data, reqd)  
2\. chama_code (Data, reqd, unique)  
3\. status (Select, reqd, options: Active\\nInactive\\nArchived, default Active)  
4\. base_currency (Link, options Currency, reqd)  
5\. timezone (Data, reqd, default Africa/Nairobi)  
6\. country (Data)  
7\. founding_date (Date)  
8\. description (Small Text)  
9\. owner_user (Link, options User)  
10\. allow_new_member_applications (Check, default 1)  
11\. default_language (Data)  
12\. archived_on (Datetime, read_only)  
<br/>Also:  
\- add validation to ensure chama_name and chama_code are unique  
\- generate the DocType JSON and the Python controller  
\- include validate() method  
\- do not use placeholders  
\- follow Frappe v16 conventions

**A-002 — Create Chama Settings DocType**

Create a custom Frappe/ERPNext v16 DocType named "Chama Settings".  
<br/>Requirements:  
\- Module: Chama Core  
\- One settings record per Chama  
\- Naming: autoname = field:chama  
\- Fields:  
1\. chama (Link, options Chama, reqd, unique)  
2\. contribution_policy_json (Long Text)  
3\. loan_policy_json (Long Text)  
4\. notification_preferences_json (Long Text)  
5\. budget_overrun_mode (Select, options: Block\\nWarn\\nAllow With Escalation, default Warn)  
6\. quorum_rules_json (Long Text)  
7\. voting_rules_json (Long Text)  
8\. exit_policy_json (Long Text)  
9\. investment_policy_json (Long Text)  
<br/>Also:  
\- create validation ensuring only one settings record per Chama  
\- create clean Frappe DocType JSON and Python controller  
\- follow ERPNext/Frappe v16 style

**A-003 — Create Chama Member DocType**

Create a custom Frappe/ERPNext v16 DocType named "Chama Member".  
<br/>Requirements:  
\- Module: Chama Core  
\- Naming: MB-.####  
\- This is the tenant-scoped member record, separate from User  
\- Fields:  
1\. user (Link, options User)  
2\. chama (Link, options Chama, reqd)  
3\. full_name (Data, reqd)  
4\. first_name (Data)  
5\. last_name (Data)  
6\. phone (Data, reqd)  
7\. email (Data)  
8\. national_id (Data, reqd)  
9\. date_of_birth (Date)  
10\. address_text (Small Text)  
11\. join_request_date (Date)  
12\. join_date (Date)  
13\. exit_date (Date)  
14\. status (Select, reqd, options: Pending\\nActive\\nSuspended\\nDormant\\nExit In Progress\\nExited\\nRejected\\nDeceased, default Pending)  
15\. primary_role (Select, options: Member\\nTreasurer\\nChair\\nSecretary\\nAuditor\\nCommittee)  
16\. active_flag (Check, default 0, read_only)  
17\. is_voting_eligible (Check, default 0)  
18\. is_loan_eligible (Check, default 0)  
19\. is_contribution_eligible (Check, default 0)  
20\. suspension_reason (Small Text)  
21\. exit_reason (Small Text)  
<br/>Validation requirements:  
\- national_id must be unique within a Chama  
\- phone should be unique within a Chama where possible  
\- if status = Active, join_date is required  
\- if exit_date is set, it cannot be earlier than join_date  
\- active_flag should be derived automatically from status  
<br/>Also:  
\- create DocType JSON and Python controller  
\- implement validate()  
\- implement helper to sync active_flag from status  
\- do not include placeholders

**A-004 — Create Chama Member Role Assignment DocType**

Create a custom Frappe/ERPNext v16 DocType named "Chama Member Role Assignment".  
<br/>Requirements:  
\- Module: Chama Core  
\- Naming: MRA-.####  
\- Purpose: track Chama-specific role assignments over time  
\- Fields:  
1\. chama (Link, options Chama, reqd)  
2\. member (Link, options Chama Member, reqd)  
3\. role_name (Select, reqd, options: Member\\nTreasurer\\nChair\\nSecretary\\nAuditor\\nCommittee)  
4\. effective_from (Date, reqd)  
5\. effective_to (Date)  
6\. active (Check, default 1)  
7\. assigned_by (Link, options User, reqd)  
8\. notes (Small Text)  
<br/>Validation:  
\- member must belong to the same Chama  
\- effective_to cannot be before effective_from  
\- for exclusive office roles (Treasurer, Chair, Secretary), optionally prevent overlapping active assignments in the same Chama  
\- if effective_to is set and is before today, active should be false  
<br/>Also:  
\- create DocType JSON and Python controller  
\- implement validate()  
\- follow Frappe v16 conventions

**A-005 — Create shared tenant validation utility**

In a custom Frappe/ERPNext v16 app, create a reusable Python utility module for Chama tenant validation.  
<br/>Requirements:  
\- Add a utility file, for example chama_core/utils/tenant.py  
\- Implement these functions:  
1\. ensure_same_chama(\*docs_or_dicts)  
2\. ensure_doc_matches_chama(doc, chama_name)  
3\. ensure_member_matches_chama(member_name, chama_name)  
4\. get_member_for_user_in_chama(user, chama_name)  
<br/>Behavior:  
\- throw frappe.ValidationError or frappe.throw with clear messages on mismatch  
\- support both Document objects and dict-like inputs where reasonable  
\- no placeholder logic  
\- clean imports and comments  
<br/>Also include example usage in comments.

**A-006 — Create active Chama context API**

Create a Frappe/ERPNext v16 whitelisted API for switching active Chama context for the logged-in user.  
<br/>Requirements:  
\- Endpoint function name suggestion: switch_active_chama  
\- Suggested module path: chama_core/api/context.py  
\- Input:  
\- chama (required)  
\- source_channel (optional: WEB, MOBILE, API)  
\- Behavior:  
1\. verify user is logged in  
2\. verify the user has access to the specified Chama through Chama Member or platform admin role  
3\. store active chama in the session or a safe user-session mechanism  
4\. create an audit/log entry of the context switch  
5\. return standard JSON-style response:  
{  
"status": "success",  
"data": {"active_chama": "..."},  
"errors": \[\]  
}  
<br/>Also:  
\- create helper function get_active_chama()  
\- reject unauthorized switches  
\- include code only, production-style, no pseudo-code

**A-007 — Create Chama Context Session log DocType**

Create a custom Frappe/ERPNext v16 DocType named "Chama Context Session".  
<br/>Requirements:  
\- Module: Chama Core  
\- Naming: CCS-.####  
\- Purpose: audit log for tenant context switches  
\- Fields:  
1\. user (Link, options User, reqd)  
2\. previous_chama (Link, options Chama)  
3\. active_chama (Link, options Chama, reqd)  
4\. switched_at (Datetime, reqd)  
5\. switched_by (Link, options User, reqd)  
6\. source_channel (Select, options: WEB\\nMOBILE\\nAPI, reqd)  
7\. session_identifier (Data)  
<br/>Also:  
\- create DocType JSON  
\- no complex controller needed unless validation is useful  
\- follow Frappe v16 conventions

**A-008 — Create permission resolution service**

Create a Python service module for resolving Chama-scoped effective permissions for a user in Frappe/ERPNext v16.  
<br/>Requirements:  
\- Suggested file: chama_core/services/permissions.py  
\- Implement:  
1\. get_active_chama_for_user(user)  
2\. get_chama_member_for_user(user, chama)  
3\. get_effective_chama_roles(user, chama)  
4\. user_can_access_chama(user, chama)  
5\. user_has_chama_role(user, chama, role_name)  
<br/>Rules:  
\- roles are resolved through Chama Member Role Assignment  
\- user must have a Chama Member record in that Chama unless platform admin logic says otherwise  
\- suspended/exited/rejected members should not get normal business roles  
\- active role assignments only  
<br/>Return clean Python structures and raise clear exceptions where needed.

**A-009 — Add common response helper for APIs**

Create a reusable response helper module for custom Frappe/ERPNext v16 APIs.  
<br/>Requirements:  
\- Suggested file: chama_core/api/responses.py  
\- Implement:  
1\. success_response(data=None, meta=None)  
2\. error_response(error_code, message, details=None, http_status_code=None)  
3\. validation_error_response(errors)  
<br/>Response shape:  
Success:  
{  
"status": "success",  
"data": {},  
"errors": \[\]  
}  
<br/>Error:  
{  
"status": "error",  
"data": null,  
"errors": \[  
{  
"error_code": "...",  
"message": "...",  
"details": {}  
}  
\]  
}  
<br/>Keep it production-ready and simple.

**A-010 — Add app-level hooks scaffold for tenant safety**

Review a Frappe/ERPNext v16 custom app and propose the minimal hooks.py entries needed for:  
\- document event hooks  
\- scheduler events scaffold  
\- permission query condition scaffold  
\- API import exposure if needed  
<br/>Context:  
This app is for a multi-tenant Chama platform and must enforce Chama isolation.  
I want a practical hooks.py baseline, not a huge speculative one.  
<br/>Output:  
\- updated hooks.py content  
\- short explanation in comments  
\- do not invent unsupported hooks