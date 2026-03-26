# PHASE B TESTING

**Phase B test data strategy**

Build data for:

- **2 active Chamas**
    - Umoja
    - Harvest
- **1 inactive Chama**
    - Jirani
- **3 contribution categories in Umoja**
- **2 contribution categories in Harvest**
- **2 monthly cycles in Umoja**
- **1 monthly cycle in Harvest**
- obligations for:
    - fully paid member
    - partially paid member
    - overdue member
    - suspended member
- payments that test:
    - exact payment
    - partial payment
    - multi-obligation allocation
    - duplicate-reference risk
    - reversal candidate

This gives you full coverage without drowning you in data.

**1\. Chamas to use**

Use your existing Phase A Chamas:

**Umoja**

- Active
- primary Phase B financial test tenant

**Harvest**

- Active
- second tenant for isolation checks

**Jirani**

- Inactive
- should not generate normal contribution activity in v1 unless you explicitly allow it

**2\. Members to use**

Reuse these from Phase A:

**Umoja**

- Grace Wanjiku — Active, Chair
- Samuel Otieno — Active, Treasurer
- Faith Njeri — Suspended
- Linda Achieng — Active, Auditor

**Harvest**

- Ann Wairimu — Active, Chair
- Samuel Otieno — Active, Member
- Faith Njeri — Active, Secretary

**Jirani**

- Joseph Mwangi — Dormant

**3\. Contribution categories to create**

**Umoja categories**

**UMOJA-CAT-1 — Shares**

- category_name: Shares
- category_code: SHR
- category_type: Shares
- amount_type: Fixed
- default_amount: 5000
- frequency: Monthly
- mandatory: 1
- allow_partial_payment: 1
- allow_future_prepayment: 0
- grace_days: 5
- active: 1
- start_date: 2026-01-01

**UMOJA-CAT-2 — Welfare**

- category_name: Welfare Fund
- category_code: WLF
- category_type: Welfare
- amount_type: Fixed
- default_amount: 1000
- frequency: Monthly
- mandatory: 1
- allow_partial_payment: 1
- allow_future_prepayment: 0
- grace_days: 3
- active: 1
- start_date: 2026-01-01

**UMOJA-CAT-3 — Emergency Levy**

- category_name: Emergency Levy
- category_code: EMG
- category_type: Levy
- amount_type: Fixed
- default_amount: 2000
- frequency: Ad Hoc
- mandatory: 0
- allow_partial_payment: 0
- allow_future_prepayment: 0
- grace_days: 2
- active: 1
- start_date: 2026-02-01

**Harvest categories**

**HARVEST-CAT-1 — Shares**

- category_name: Shares
- category_code: SHR
- category_type: Shares
- amount_type: Fixed
- default_amount: 3000
- frequency: Monthly
- mandatory: 1
- allow_partial_payment: 1
- allow_future_prepayment: 0
- grace_days: 5
- active: 1
- start_date: 2026-01-01

**HARVEST-CAT-2 — Welfare**

- category_name: Welfare
- category_code: WLF
- category_type: Welfare
- amount_type: Fixed
- default_amount: 500
- frequency: Monthly
- mandatory: 1
- allow_partial_payment: 1
- allow_future_prepayment: 0
- grace_days: 3
- active: 1
- start_date: 2026-01-01

**4\. Contribution cycles to create**

Use dates relative to your current system date if needed, but keep them realistic.

**Umoja cycles**

**UMOJA-FEB-2026**

- cycle_name: UMOJA-FEB-2026
- period_start: 2026-02-01
- period_end: 2026-02-28
- frequency: Monthly
- status: Generated

**UMOJA-MAR-2026**

- cycle_name: UMOJA-MAR-2026
- period_start: 2026-03-01
- period_end: 2026-03-31
- frequency: Monthly
- status: Generated

**Harvest cycle**

**HARVEST-MAR-2026**

- cycle_name: HARVEST-MAR-2026
- period_start: 2026-03-01
- period_end: 2026-03-31
- frequency: Monthly
- status: Generated

**5\. Contribution obligations to create**

This is the important part.

**Umoja — February 2026 obligations**

**Grace (Active, full payer scenario)**

1.  Shares

- amount_due: 5000
- amount_paid: 5000
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-02-05
- grace_end_date: 2026-02-10
- status: Paid

1.  Welfare Fund

- amount_due: 1000
- amount_paid: 1000
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-02-05
- grace_end_date: 2026-02-08
- status: Paid

**Samuel (partial + overdue scenario)**

1.  Shares

- amount_due: 5000
- amount_paid: 3000
- amount_waived: 0
- amount_outstanding: 2000
- due_date: 2026-02-05
- grace_end_date: 2026-02-10
- status: Overdue

1.  Welfare Fund

- amount_due: 1000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 1000
- due_date: 2026-02-05
- grace_end_date: 2026-02-08
- status: Overdue

**Faith (Suspended member with historical obligation)**

1.  Shares

- amount_due: 5000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 5000
- due_date: 2026-02-05
- grace_end_date: 2026-02-10
- status: Overdue

**Linda (waiver scenario)**

1.  Welfare Fund

- amount_due: 1000
- amount_paid: 0
- amount_waived: 1000
- amount_outstanding: 0
- due_date: 2026-02-05
- grace_end_date: 2026-02-08
- status: Waived

**Umoja — March 2026 obligations**

**Grace**

1.  Shares

- amount_due: 5000
- amount_paid: 5000
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-03-05
- grace_end_date: 2026-03-10
- status: Paid

1.  Welfare Fund

- amount_due: 1000
- amount_paid: 1000
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-03-05
- grace_end_date: 2026-03-08
- status: Paid

**Samuel**

1.  Shares

- amount_due: 5000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 5000
- due_date: 2026-03-05
- grace_end_date: 2026-03-10
- status: Due

1.  Welfare Fund

- amount_due: 1000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 1000
- due_date: 2026-03-05
- grace_end_date: 2026-03-08
- status: Due

**Linda**

1.  Shares

- amount_due: 5000
- amount_paid: 2500
- amount_waived: 0
- amount_outstanding: 2500
- due_date: 2026-03-05
- grace_end_date: 2026-03-10
- status: Partially Paid

1.  Welfare Fund

- amount_due: 1000
- amount_paid: 1000
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-03-05
- grace_end_date: 2026-03-08
- status: Paid

**Emergency Levy (ad hoc)**

1.  Grace

- amount_due: 2000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 2000
- due_date: 2026-03-12
- grace_end_date: 2026-03-14
- status: Due

1.  Samuel

- amount_due: 2000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 2000
- due_date: 2026-03-12
- grace_end_date: 2026-03-14
- status: Due

**Harvest — March 2026 obligations**

**Ann**

1.  Shares

- amount_due: 3000
- amount_paid: 3000
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-03-06
- grace_end_date: 2026-03-11
- status: Paid

1.  Welfare

- amount_due: 500
- amount_paid: 500
- amount_waived: 0
- amount_outstanding: 0
- due_date: 2026-03-06
- grace_end_date: 2026-03-09
- status: Paid

**Samuel**

1.  Shares

- amount_due: 3000
- amount_paid: 1000
- amount_waived: 0
- amount_outstanding: 2000
- due_date: 2026-03-06
- grace_end_date: 2026-03-11
- status: Partially Paid

1.  Welfare

- amount_due: 500
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 500
- due_date: 2026-03-06
- grace_end_date: 2026-03-09
- status: Due

**Faith**

1.  Shares

- amount_due: 3000
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 3000
- due_date: 2026-03-06
- grace_end_date: 2026-03-11
- status: Due

1.  Welfare

- amount_due: 500
- amount_paid: 0
- amount_waived: 0
- amount_outstanding: 500
- due_date: 2026-03-06
- grace_end_date: 2026-03-09
- status: Due

**6\. Payments to create**

Now create payment events that produce useful allocation tests.

**Umoja payments**

**Payment U-001 — Grace full February payment**

- member: Grace
- payment_date: 2026-02-04 09:15:00
- amount_received: 6000
- payment_method: Mobile Money
- payment_reference: UMOJA-MP-0001
- source_channel: Desk
- status after allocation: Allocated

Expected allocation:

- 5000 → Grace Feb Shares
- 1000 → Grace Feb Welfare

**Payment U-002 — Samuel partial February payment**

- member: Samuel
- payment_date: 2026-02-07 10:20:00
- amount_received: 3000
- payment_method: Bank
- payment_reference: UMOJA-BK-0001
- source_channel: Desk
- status after allocation: Allocated

Expected allocation:

- 3000 → Samuel Feb Shares

**Payment U-003 — Grace full March payment**

- member: Grace
- payment_date: 2026-03-04 08:00:00
- amount_received: 6000
- payment_method: Mobile Money
- payment_reference: UMOJA-MP-0002
- source_channel: Mobile
- status after allocation: Allocated

Expected allocation:

- 5000 → Grace Mar Shares
- 1000 → Grace Mar Welfare

**Payment U-004 — Linda mixed partial March payment**

- member: Linda
- payment_date: 2026-03-06 14:10:00
- amount_received: 3500
- payment_method: Cash
- payment_reference: null
- source_channel: Desk
- status after allocation: Allocated

Expected allocation:

- 2500 → Linda Mar Shares
- 1000 → Linda Mar Welfare

**Payment U-005 — Samuel late multi-obligation payment candidate**

- member: Samuel
- payment_date: 2026-03-15 11:45:00
- amount_received: 4000
- payment_method: Mobile Money
- payment_reference: UMOJA-MP-0003
- source_channel: API
- status after allocation: Partially Allocated or Allocated depending on live state

Expected oldest-first allocation:

1.  Samuel Feb Welfare overdue = 1000
2.  Samuel Feb Shares overdue remaining = 2000
3.  Samuel Mar Welfare due = 1000  
    Total = 4000

This is your **best allocation engine test**.

**Payment U-006 — suspected duplicate reference test**

- member: Samuel
- payment_date: 2026-03-15 11:47:00
- amount_received: 4000
- payment_method: Mobile Money
- payment_reference: UMOJA-MP-0003
- source_channel: API
- duplicate_flag: should be set by detection helper

This should **not necessarily be blocked**, but should be flagged.

**Payment U-007 — reversal candidate**

- member: Grace
- payment_date: 2026-03-13 09:30:00
- amount_received: 2000
- payment_method: Mobile Money
- payment_reference: UMOJA-MP-LEVY-01
- source_channel: Desk
- intended allocation:
    - 2000 → Grace Emergency Levy
- later use this one for reversal testing

**Harvest payments**

**Payment H-001 — Ann full March payment**

- member: Ann
- payment_date: 2026-03-05 09:00:00
- amount_received: 3500
- payment_method: Mobile Money
- payment_reference: HARVEST-MP-0001
- source_channel: Desk
- status after allocation: Allocated

Expected allocation:

- 3000 → Ann Shares
- 500 → Ann Welfare

**Payment H-002 — Samuel partial March payment**

- member: Samuel
- payment_date: 2026-03-08 13:00:00
- amount_received: 1000
- payment_method: Bank
- payment_reference: HARVEST-BK-0001
- source_channel: Desk
- status after allocation: Allocated

Expected allocation:

- 1000 → Samuel Shares

**7\. What this dataset allows you to test**

This is why this set is good.

**Allocation tests**

- exact full payment
- partial payment
- oldest-first across multiple obligations
- cross-category allocation
- ad hoc levy payment
- reversal candidate

**Status tests**

- Paid
- Partially Paid
- Due
- Overdue
- Waived

**Tenant tests**

- Umoja and Harvest both have Shares and Welfare categories
- same member name/user appears across Chamas
- allocations must never cross tenant boundaries

**Role/status tests**

- Suspended member has historical obligation
- Active members receive normal obligations
- Inactive Chama does not participate in Phase B generation

**Reporting tests**

- compliance report
- overdue report
- payment register
- member contribution statement

**8\. Expected summary totals you can use as checkpoints**

Use these to verify reports and APIs.

**Umoja expected totals**

**February obligations**

- Grace: 6000 due, 6000 paid, 0 outstanding
- Samuel: 6000 due, 3000 paid initially, 3000 outstanding initially
- Faith: 5000 due, 0 paid, 5000 outstanding
- Linda: 1000 due, 1000 waived, 0 outstanding

Initial February totals before U-005:

- due = 18000
- paid = 9000
- waived = 1000
- outstanding = 8000

After U-005 allocation of 4000 to Samuel:

- Samuel Feb outstanding becomes 0
- February totals become:
    - due = 18000
    - paid = 13000
    - waived = 1000
    - outstanding = 4000

**March Umoja obligations before U-005 and U-007**

- Grace: 8000 due (6000 regular + 2000 levy), 6000 paid before levy payment, 2000 outstanding
- Samuel: 8000 due (6000 regular + 2000 levy), 0 paid before U-005, 8000 outstanding
- Linda: 6000 due, 3500 paid, 2500 outstanding

March Umoja totals before U-005 and U-007:

- due = 22000
- paid = 9500
- outstanding = 12500

After U-005:

- Samuel Mar Welfare gets 1000
- Samuel Mar Shares still 5000 outstanding
- Samuel Mar Levy still 2000 outstanding

After U-007:

- Grace levy becomes paid

These are good checkpoints for report comparison.

**Harvest March totals**

- Ann: 3500 due, 3500 paid, 0 outstanding
- Samuel: 3500 due, 1000 paid, 2500 outstanding
- Faith: 3500 due, 0 paid, 3500 outstanding

Harvest March totals:

- due = 10500
- paid = 4500
- outstanding = 6000

**9\. Suggested Phase B release-gate scenarios using this data**

Once seeded, test these before moving to Phase C:

1.  **Umoja summary for Samuel** shows:
    - overdue cleared for Feb after U-005
    - March partial allocations correct
2.  **Harvest summary for Samuel** stays completely separate:
    - no Umoja payments affect Harvest obligations
3.  **Duplicate flag** is raised for U-006
4.  **Reversal of U-007** restores Grace levy outstanding to 2000
5.  **Faith in Umoja** remains with historical obligation despite Suspended status
6.  **Waived Linda Feb Welfare** stays waived and is not treated as overdue
7.  **Reports match obligations table exactly**
    - compliance
    - overdue
    - payment register
    - member statement