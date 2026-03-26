**PHASE A TESTING**

**1\. Phase A release gate**

Phase A passes only if all of these are true:

1.  A user can belong to more than one Chama.
2.  The same user can have different roles in different Chamas.
3.  Switching active Chama changes visible data and effective permissions.
4.  Records from one Chama never appear in another Chama context.
5.  A user cannot switch into a Chama they do not belong to.
6.  Suspended or exited members do not get normal business access in that Chama.
7.  Exclusive roles do not overlap where your rules say they cannot.
8.  Every context switch creates an audit log entry.
9.  Every Chama-owned record created in-context is stamped with the correct chama.
10. Direct access to another Chama’s record is blocked even if the URL or API call is guessed.

**2\. Realistic sample data**

Use **3 Chamas**, **7 users**, and **8 member records**.

**2.1 Chamas**

**CH-0001**

- chama_name: Umoja Women Investment Group
- chama_code: UMOJA
- status: Active
- base_currency: KES
- timezone: Africa/Nairobi
- country: Kenya
- allow_new_member_applications: 1

**CH-0002**

- chama_name: Harvest Welfare Circle
- chama_code: HARVEST
- status: Active
- base_currency: KES
- timezone: Africa/Nairobi
- country: Kenya
- allow_new_member_applications: 1

**CH-0003**

- chama_name: Jirani Land Pool
- chama_code: JIRANI
- status: Inactive
- base_currency: KES
- timezone: Africa/Nairobi
- country: Kenya
- allow_new_member_applications: 0

**2.2 Users**

Create these ERPNext users:

1.  grace@umoja.test
2.  samuel@shared.test
3.  ann@harvest.test
4.  joseph@jirani.test
5.  faith@ops.test
6.  linda@audit.test
7.  outsider@none.test

You can also create a platform admin user if you want to test support/admin behavior separately:  
8\. platform.admin@test

**2.3 Chama Members**

**In CH-0001 Umoja**

**MB-0001**

- user: grace@umoja.test
- full_name: Grace Wanjiku
- phone: +254700100001
- email: grace@umoja.test
- national_id: 29001111
- status: Active
- join_date: 2024-02-10
- primary_role: Chair

**MB-0002**

- user: samuel@shared.test
- full_name: Samuel Otieno
- phone: +254700100002
- email: samuel@shared.test
- national_id: 30112233
- status: Active
- join_date: 2024-03-01
- primary_role: Treasurer

**MB-0003**

- user: faith@ops.test
- full_name: Faith Njeri
- phone: +254700100003
- email: faith@ops.test
- national_id: 31223344
- status: Suspended
- join_date: 2024-05-15
- primary_role: Member
- suspension_reason: Non-compliance with agreed rules

**MB-0004**

- user: linda@audit.test
- full_name: Linda Achieng
- phone: +254700100004
- email: linda@audit.test
- national_id: 32334455
- status: Active
- join_date: 2024-06-20
- primary_role: Auditor

**In CH-0002 Harvest**

**MB-0005**

- user: ann@harvest.test
- full_name: Ann Wairimu
- phone: +254711200001
- email: ann@harvest.test
- national_id: 33445566
- status: Active
- join_date: 2024-01-12
- primary_role: Chair

**MB-0006**

- user: samuel@shared.test
- full_name: Samuel Otieno
- phone: +254711200002
- email: samuel@shared.test
- national_id: 30112233
- status: Active
- join_date: 2024-04-05
- primary_role: Member

**MB-0007**

- user: faith@ops.test
- full_name: Faith Njeri
- phone: +254711200003
- email: faith@ops.test
- national_id: 31223344
- status: Active
- join_date: 2024-07-01
- primary_role: Secretary

**In CH-0003 Jirani**

**MB-0008**

- user: joseph@jirani.test
- full_name: Joseph Mwangi
- phone: +254722300001
- email: joseph@jirani.test
- national_id: 34556677
- status: Dormant
- join_date: 2023-09-10
- primary_role: Member

This set is good because:

- samuel@shared.test belongs to 2 Chamas with different roles
- faith@ops.test is Suspended in one Chama and Active in another
- one Chama is Inactive
- one outsider user belongs to none

**2.4 Role assignments**

Create role assignments explicitly.

**CH-0001**

- Grace Wanjiku → Chair → active
- Samuel Otieno → Treasurer → active
- Linda Achieng → Auditor → active
- Faith Njeri → Member → active assignment exists, but member status Suspended

**CH-0002**

- Ann Wairimu → Chair → active
- Samuel Otieno → Member → active
- Faith Njeri → Secretary → active

**CH-0003**

- Joseph Mwangi → Member → active

This lets you test:

- different roles per Chama
- status overriding role
- inactive tenant handling

**2.5 Chama settings**

Create one settings row per Chama.

**Umoja**

- budget_overrun_mode: Warn

**Harvest**

- budget_overrun_mode: Block

**Jirani**

- budget_overrun_mode: Allow With Escalation

This helps verify settings are tenant-specific.

**3\. Test scenarios for the Phase A gate**

Use the dataset above and run these cases.

**Test A1 — Multi-Chama membership works**

**User:** samuel@shared.test

Expected:

- can see both Umoja and Harvest in “My Chamas”
- cannot see Jirani
- active role in Umoja = Treasurer
- active role in Harvest = Member

Pass condition:

- both memberships resolve correctly and separately

**Test A2 — Same user, different roles per Chama**

**User:** samuel@shared.test

Steps:

1.  switch context to Umoja
2.  fetch effective Chama roles
3.  switch to Harvest
4.  fetch effective Chama roles again

Expected:

- Umoja: Treasurer
- Harvest: Member

Pass condition:

- role resolution changes with active Chama

**Test A3 — Suspended in one Chama, active in another**

**User:** faith@ops.test

Steps:

1.  switch to Umoja
2.  check effective roles / allowed actions
3.  switch to Harvest
4.  check effective roles / allowed actions

Expected:

- Umoja: membership visible but normal business access restricted due to Suspended
- Harvest: Secretary access valid

Pass condition:

- status is tenant-scoped and overrides role only in the affected Chama

**Test A4 — Outsider cannot switch into any Chama**

**User:** outsider@none.test

Steps:

1.  call switch context for Umoja
2.  call switch context for Harvest

Expected:

- both rejected with authorization/context error

Pass condition:

- no context switch allowed

**Test A5 — Inactive Chama handling**

**User:** joseph@jirani.test

Steps:

1.  attempt switch into Jirani
2.  fetch allowed operations

Expected:

- depending on your Phase A design:
    - either switch blocked because tenant is Inactive
    - or switch allowed in readonly mode only

Pass condition:

- behavior is explicit and consistent

**Test A6 — Exclusive role conflict blocked**

In Umoja, try assigning another active Treasurer while Samuel is still active Treasurer.

Example:

- assign Grace Wanjiku → Treasurer effective today

Expected:

- blocked if Treasurer is configured as exclusive
- or previous assignment must be ended first

Pass condition:

- no overlapping exclusive office role

**Test A7 — Cross-Chama direct record access blocked**

**User:** samuel@shared.test

Steps:

1.  switch to Umoja
2.  try to fetch Ann Wairimu’s Harvest member record directly by name or URL/API
3.  try to fetch Harvest role assignment directly

Expected:

- blocked or not found in current context

Pass condition:

- record-level tenant protection works even when ID is known

**Test A8 — Context switch audit log created**

Use samuel@shared.test.

Steps:

1.  switch Umoja → Harvest
2.  switch Harvest → Umoja

Expected:

- 2 Chama Context Session records
- each has:
    - user
    - previous_chama
    - active_chama
    - switched_at
    - source_channel

Pass condition:

- audit records are accurate

**Test A9 — New in-context record stamps correct Chama**

Once context is Umoja, create a harmless tenant-owned record such as:

- Chama Member Role Assignment  
    or any early tenant-owned support record

Expected:

- new record stamped chama = CH-0001

Then switch to Harvest and repeat.

Pass condition:

- no record created under wrong tenant

**Test A10 — Chama Settings isolation**

Steps:

1.  fetch Umoja settings in Umoja context
2.  switch to Harvest
3.  fetch Harvest settings
4.  try direct access to Umoja settings while in Harvest context

Expected:

- first two work correctly
- cross-context direct access blocked

Pass condition:

- settings do not leak across tenants

**4\. Suggested seed data format**

If you want a simple manual seeding order, use this sequence:

1.  Create users
2.  Create Chamas
3.  Create Chama Settings
4.  Create Chama Members
5.  Create Role Assignments
6.  Test context switching
7.  Test permissions

**5\. Minimal expected test outputs**

After seeding, these should be true:

**samuel@shared.test**

- accessible Chamas: 2
- Umoja role: Treasurer
- Harvest role: Member

**faith@ops.test**

- Umoja status: Suspended
- Harvest status: Active
- Umoja normal business permissions: blocked/restricted
- Harvest secretary permissions: allowed

**outsider@none.test**

- accessible Chamas: 0
- context switch attempts: rejected

**joseph@jirani.test**

- accessible Chamas: Jirani only
- if Inactive tenant blocked: switch denied
- if readonly allowed: no write actions allowed

**6\. Quick manual release-gate checklist**

Phase A is ready only if you can honestly mark all of these yes:

- Same user can belong to 2 Chamas
- Same user resolves different roles by Chama
- Suspended in one Chama does not spill into another
- Outsider cannot switch into any Chama
- Inactive Chama behavior is explicit and correct
- Exclusive role conflict is prevented
- Known record IDs from another Chama are blocked
- Context switch audit log is created every time
- All newly created tenant-owned records stamp the active Chama
- Chama settings are isolated