**UI ORGANIZATION FOR TESTING**

**General instruction for Cursor before all workspace tasks**

Use this once at the top of your Cursor chat before individual prompts:

Context:  
This is a Frappe/ERPNext v16 app named \`chama\` for a multi-tenant Chama platform.  
I want temporary internal workspaces for developer/testing use during implementation.  
These are not final UX screens.  
Use native Frappe Workspace features and follow v16 conventions.  
Prefer creating/updating Workspace records in a clean, repeatable way that can be committed to the repo.  
Do not invent unsupported block types.  
Keep labels explicit and practical for QA/testing.

**Prompt 1 — Create Nexus QA Home workspace**

Create a repeatable Frappe/ERPNext v16 implementation for a workspace named "Nexus QA Home" in app \`chama\`.  
<br/>Goal:  
This is the top-level internal workspace for developer/testing navigation.  
It should be practical, not polished.  
<br/>Requirements:  
\- Workspace title: Nexus QA Home  
\- Public: No  
\- For internal authenticated users only  
\- Content should be organized into clear sections using supported workspace blocks  
\- Prefer shortcuts and number cards  
\- Do not use unsupported block types  
<br/>Sections and shortcuts:  
<br/>1\. Build Status  
Shortcuts:  
\- Foundation  
\- Contributions  
\- Reports  
\- Test Utilities  
\- Loans (Phase C)  
\- Disbursements (Phase D)  
\- Reconciliation (Phase E)  
\- Notifications (Phase F)  
<br/>2\. Core Master Data  
Shortcuts:  
\- Chama  
\- Chama Settings  
\- Chama Member  
\- Chama Member Role Assignment  
<br/>3\. Current Financial Engine  
Shortcuts:  
\- Chama Contribution Category  
\- Chama Contribution Cycle  
\- Chama Contribution Obligation  
\- Chama Contribution Payment  
<br/>4\. Quick Reports  
Shortcuts:  
\- Contribution Compliance Report  
\- Overdue Contributions Report  
\- Payment Register  
\- Member Contribution Statement  
<br/>5\. Health Snapshot  
Number card placeholders or references for:  
\- Active Chamas  
\- Active Members  
\- Suspended Members  
\- Open Contribution Obligations  
\- Overdue Contribution Obligations  
\- Payments Today  
<br/>6\. Recent Activity  
Shortcut/filter placeholders or quick access for:  
\- Recent Payments  
\- Recent Context Switches  
\- Recent Obligations  
\- Recently Created Members  
<br/>What I want from you:  
\- the best implementation approach for Frappe v16 (workspace record / fixture / setup utility)  
\- code/files needed  
\- practical block/shortcut structure  
\- production-style code only  
\- no pseudo-code

**Prompt 2 — Create Foundation workspace**

Create a repeatable Frappe/ERPNext v16 workspace named "Foundation" for app \`chama\`.  
<br/>Goal:  
Internal testing workspace for Phase A foundation and tenant controls.  
<br/>Requirements:  
\- Workspace title: Foundation  
\- Internal only  
\- Organize into sections using supported workspace blocks  
<br/>Sections:  
<br/>1\. Master Tenant Setup  
Shortcuts:  
\- Chama  
\- Chama Settings  
<br/>2\. Membership  
Shortcuts:  
\- Chama Member  
\- Chama Member Role Assignment  
<br/>3\. Tenant Audit  
Shortcuts:  
\- Chama Context Session  
<br/>4\. Useful Filtered Views  
Create shortcut placeholders or filtered list shortcuts for:  
\- Active Chamas  
\- Inactive Chamas  
\- Active Members  
\- Suspended Members  
\- Dormant Members  
<br/>5\. Number Cards  
Add placeholders/references for:  
\- Total Chamas  
\- Active Chamas  
\- Total Members  
\- Suspended Members  
\- Dormant Members  
\- Context Switches Today  
<br/>6\. Release Gate Panel  
Add shortcuts or placeholders titled:  
\- Test A1 Multi-Chama Membership  
\- Test A2 Role by Chama  
\- Test A3 Suspended vs Active  
\- Test A4 Outsider Access  
\- Test A7 Cross-Chama Record Access  
\- Test A8 Context Audit  
<br/>Implementation constraints:  
\- use native Frappe Workspace support  
\- make it repeatable and repo-friendly  
\- no unsupported blocks  
\- no hand-wavy instructions  
<br/>Output:  
\- files/code needed  
\- recommended fixture/setup approach  
\- exact workspace content structure

**Prompt 3 — Create Contributions workspace**

Create a repeatable Frappe/ERPNext v16 workspace named "Contributions" for app \`chama\`.  
<br/>Goal:  
This is the primary internal testing workspace for Phase B contribution flows.  
<br/>Requirements:  
\- Workspace title: Contributions  
\- Internal only  
\- Organized with supported workspace blocks  
\- Focus on operational testing and quick debugging  
<br/>Sections:  
<br/>1\. Setup  
Shortcuts:  
\- Chama Contribution Category  
\- Chama Contribution Cycle  
<br/>2\. Transactions  
Shortcuts:  
\- Chama Contribution Obligation  
\- Chama Contribution Payment  
<br/>3\. Reports  
Shortcuts:  
\- Contribution Compliance Report  
\- Overdue Contributions Report  
\- Payment Register  
\- Member Contribution Statement  
<br/>4\. Filtered Action Views  
Add shortcut placeholders or filtered list shortcuts for:  
\- Due Obligations  
\- Overdue Obligations  
\- Partially Paid Obligations  
\- Paid Obligations  
\- Waived Obligations  
\- Recorded Payments  
\- Allocated Payments  
\- Partially Allocated Payments  
\- Flagged Payments  
\- Reversed Payments  
<br/>5\. Number Cards  
Add placeholders/references for:  
\- Total Obligations in Current Chama  
\- Due Obligations  
\- Overdue Obligations  
\- Partially Paid Obligations  
\- Total Outstanding  
\- Payments Today  
\- Flagged Payments  
<br/>6\. Seed/Test Scenarios  
Add shortcuts/placeholders titled:  
\- Grace Feb Obligations  
\- Samuel Umoja Obligations  
\- Linda Waived Obligation  
\- Grace Levy Payment  
\- Duplicate Payment Reference Checks  
\- Harvest Samuel Obligations  
<br/>7\. Recent Operational Lists  
Shortcuts/placeholders:  
\- Recent Payments  
\- Recent Obligations  
\- Overdue Obligations Sorted by Due Date  
\- Payments Missing Reference  
<br/>Implementation constraints:  
\- use native Frappe v16 workspace capabilities  
\- repo-friendly repeatable approach  
\- no unsupported block types  
<br/>Output:  
\- code/files needed  
\- exact recommended structure  
\- practical implementation only

**Prompt 4 — Create Reports workspace**

Create a repeatable Frappe/ERPNext v16 workspace named "Reports" for app \`chama\`.  
<br/>Goal:  
Central internal reporting workspace for current implemented features.  
<br/>Requirements:  
\- Workspace title: Reports  
\- Internal only  
\- Use supported workspace blocks  
<br/>Sections:  
<br/>1\. Contribution Reports  
Shortcuts:  
\- Contribution Compliance Report  
\- Overdue Contributions Report  
\- Payment Register  
\- Member Contribution Statement  
<br/>2\. Foundation/Admin Reports  
Add placeholders or shortcuts for future reports:  
\- Multi-Chama Access Report  
\- Membership Status Report  
\- Role Assignment History  
<br/>3\. Comparison / QA Links  
Add shortcuts/placeholders titled:  
\- Compare Summary API vs Compliance Report  
\- Compare Payment Register vs Payment List  
\- Compare Member Statement vs Obligation List  
<br/>4\. Reporting Utilities  
Add placeholders or shortcuts for:  
\- Saved Reports  
\- Favorites  
\- Report Debug / Validation (placeholder)  
<br/>5\. Number Cards (minimal)  
\- Reports Available  
\- Saved Report Views  
<br/>Implementation constraints:  
\- native Frappe workspace only  
\- practical and repeatable  
\- keep it simple  
\- no pseudo-code  
<br/>Output:  
\- code/files needed  
\- workspace structure

**Prompt 5 — Create Test Utilities workspace**

Create a repeatable Frappe/ERPNext v16 workspace named "Test Utilities" for app \`chama\`.  
<br/>Goal:  
Internal-only developer and tester workspace for seed/test/integrity navigation.  
<br/>Requirements:  
\- Workspace title: Test Utilities  
\- Internal/admin-only orientation  
\- Supported workspace blocks only  
<br/>Sections:  
<br/>1\. Seed / Test References  
Add shortcuts/placeholders titled:  
\- Phase A Seed Reference  
\- Phase B Seed Reference  
\- Phase A Test Rig  
\- Phase B Test Rig  
<br/>2\. Diagnostics  
Shortcuts/placeholders:  
\- Flagged Payments  
\- Suspended Members  
\- Cross-Chama Audit Logs  
\- Context Sessions Today  
<br/>3\. Integrity Checks  
Shortcuts/placeholders:  
\- Records Missing Chama  
\- Mismatched Member/Chama Links  
\- Duplicate Payment References  
\- Orphan Role Assignments  
<br/>4\. Developer Notes  
Add a shortcut or placeholder for:  
\- Current Test Commands  
\- Current Release Gate Status  
\- Known Issues  
\- Next Phase Tasks  
<br/>Implementation constraints:  
\- native Frappe workspace only  
\- repo-friendly  
\- practical, not polished  
<br/>Output:  
\- code/files needed  
\- recommended implementation approach  
\- exact structure

**Prompt 6 — Create empty phase-shell workspaces**

Use one prompt for all 4 shells.

Create repeatable Frappe/ERPNext v16 workspace shells for app \`chama\` with these titles:  
<br/>\- Loans (Phase C)  
\- Disbursements (Phase D)  
\- Reconciliation (Phase E)  
\- Notifications (Phase F)  
<br/>Goal:  
These are temporary empty module shells so the Desk navigation matches the implementation roadmap.  
<br/>Requirements for each workspace:  
\- internal only  
\- simple title section  
\- one placeholder section named "Planned Artifacts"  
\- one placeholder section named "Phase Status"  
\- include sensible shortcut placeholders only, without referencing non-existent DocTypes if that would break setup  
\- keep implementation minimal and clean  
<br/>Expected planned artifacts:  
<br/>Loans (Phase C):  
\- Loan List  
\- Chama Guarantor  
\- Loan Portfolio Report  
\- Overdue Loans Report  
<br/>Disbursements (Phase D):  
\- Disbursement Request  
\- Disbursement Execution  
\- Disbursement Register  
<br/>Reconciliation (Phase E):  
\- Financial Period  
\- Reconciliation Run  
\- Reconciliation Issue  
\- Reconciliation Summary  
<br/>Notifications (Phase F):  
\- Notification Event  
\- Notification Queue  
\- Notification Inbox  
\- Notification Failures  
<br/>Output:  
\- repeatable code/files  
\- practical workspace shell implementation

**Prompt 7 — Generate supporting Number Cards**

Do this after the workspaces exist.

Create Frappe/ERPNext v16 Number Card definitions or the recommended repeatable implementation for these internal workspace metrics in app \`chama\`.  
<br/>Current implemented modules:  
\- Foundation  
\- Contributions  
<br/>I need number cards for:  
1\. Active Chamas  
2\. Active Members  
3\. Suspended Members  
4\. Open Contribution Obligations  
5\. Overdue Contribution Obligations  
6\. Payments Today  
7\. Flagged Payments  
8\. Total Outstanding Contributions  
<br/>Requirements:  
\- tenant-safe where applicable  
\- practical for internal QA use  
\- use existing DocTypes from current implementation  
\- recommend the correct card type/query approach for Frappe v16  
\- repo-friendly repeatable setup  
\- no pseudo-code

**Prompt 8 — Generate filtered shortcuts / saved list patterns**

Do this after the workspaces exist and after you see what Cursor generated.

For app \`chama\` on Frappe/ERPNext v16, generate the best repeatable implementation approach for filtered workspace shortcuts or saved list views for the following internal QA targets.  
<br/>DocTypes already exist:  
\- Chama Member  
\- Chama Contribution Obligation  
\- Chama Contribution Payment  
\- Chama Context Session  
<br/>I need filtered navigation targets for:  
<br/>Chama Member:  
\- Active Members  
\- Suspended Members  
\- Dormant Members  
<br/>Chama Contribution Obligation:  
\- Due Obligations  
\- Overdue Obligations  
\- Partially Paid  
\- Paid  
\- Waived  
\- Umoja Obligations  
\- Harvest Obligations  
\- Samuel Umoja Obligations  
\- Samuel Harvest Obligations  
<br/>Chama Contribution Payment:  
\- Recorded Payments  
\- Allocated Payments  
\- Partially Allocated Payments  
\- Flagged Payments  
\- Reversed Payments  
\- Today’s Payments  
\- Umoja Payments  
\- Harvest Payments  
<br/>Chama Context Session:  
\- Today’s Context Switches  
\- Samuel Context Switches  
<br/>Requirements:  
\- recommend whether to use workspace shortcuts with filters, saved reports, list customizations, or another native Frappe v16 approach  
\- keep it repeatable and repo-friendly  
\- do not suggest manual click-only setup unless unavoidable

**Recommended execution order**

Do them in this order:

1.  Prompt 1 — Nexus QA Home
2.  Prompt 2 — Foundation
3.  Prompt 3 — Contributions
4.  Prompt 4 — Reports
5.  Prompt 5 — Test Utilities
6.  Prompt 6 — phase shells
7.  Prompt 7 — Number Cards
8.  Prompt 8 — filtered shortcuts

That gives you:

- navigation first
- metrics second
- refined testing entry points last