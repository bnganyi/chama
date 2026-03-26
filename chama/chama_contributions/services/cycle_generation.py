"""
Cycle Generation Service — creates monthly/periodic cycles and their obligations.

Daily scheduler entry point: generate_due_cycles_for_today()

Idempotency guards:
- A cycle is not created if one with the same chama + period_start + period_end + frequency exists.
- An obligation is not created if one with the same member + contribution_category + cycle exists.
"""

import frappe
from frappe.utils import flt, today, add_days, getdate, nowdate, nowdatetime


ACTIVE_MEMBER_STATUSES = {"Active"}
CYCLE_GENERATING_CHAMA_STATUSES = {"Active"}


def get_active_categories(chama, target_date):
    """
    Return active contribution categories for a Chama on a given date.
    Ad Hoc categories are excluded from scheduled cycle generation.
    """
    target_date_str = str(target_date)
    categories = frappe.get_all(
        "Chama Contribution Category",
        filters={
            "chama": chama,
            "active": 1,
            "frequency": ("!=", "Ad Hoc"),
            "start_date": ("<=", target_date_str),
        },
        fields=["name", "category_name", "amount_type", "default_amount", "frequency", "grace_days"],
    )
    # Exclude categories that have ended
    active = []
    for cat in categories:
        end_date = frappe.db.get_value("Chama Contribution Category", cat.name, "end_date")
        if end_date and str(end_date) < target_date_str:
            continue
        active.append(cat)
    return active


def get_eligible_members(chama, target_date):
    """Return Active members of the Chama who are eligible for obligations."""
    members = frappe.get_all(
        "Chama Member",
        filters={"chama": chama, "status": ("in", list(ACTIVE_MEMBER_STATUSES))},
        fields=["name", "full_name", "join_date"],
    )
    target = getdate(target_date)
    return [m for m in members if m.join_date and getdate(m.join_date) <= target]


def resolve_category_amount(category_doc, member_doc, target_date):
    """
    Resolve the obligation amount for a member on a given category.

    Currently supports Fixed only. Variable categories log a warning and return 0.
    """
    if category_doc.get("amount_type") == "Fixed":
        return flt(category_doc.get("default_amount", 0))
    frappe.logger().warning(
        f"Variable amount type not yet supported for category {category_doc.get('name')}. Skipping."
    )
    return 0


def create_cycle(chama, period_start, period_end, frequency, generated_by=None):
    """
    Create a Chama Contribution Cycle if one does not already exist.

    Returns:
        tuple: (cycle_name, created_flag)
    """
    existing = frappe.db.get_value(
        "Chama Contribution Cycle",
        {
            "chama": chama,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "frequency": frequency,
        },
        "name",
    )
    if existing:
        return existing, False

    cycle_label = f"{chama[:6].upper()}-{str(period_start)[:7].replace('-', '')}"
    cycle = frappe.get_doc(
        {
            "doctype": "Chama Contribution Cycle",
            "chama": chama,
            "cycle_name": cycle_label,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "frequency": frequency,
            "status": "Generated",
            "generated_on": nowdatetime(),
            "generated_by": generated_by or frappe.session.user,
        }
    )
    cycle.insert(ignore_permissions=True)
    frappe.db.commit()
    return cycle.name, True


def generate_obligations_for_cycle(cycle_name):
    """
    Generate obligation records for all eligible members and active categories
    in the given cycle's Chama and period.

    Returns:
        dict: {created: int, skipped: int}
    """
    cycle = frappe.get_doc("Chama Contribution Cycle", cycle_name)
    chama = cycle.chama
    period_start = getdate(cycle.period_start)

    categories = get_active_categories(chama, period_start)
    members = get_eligible_members(chama, period_start)

    created = 0
    skipped = 0

    for member in members:
        for cat in categories:
            existing = frappe.db.get_value(
                "Chama Contribution Obligation",
                {
                    "member": member.name,
                    "contribution_category": cat.name,
                    "cycle": cycle_name,
                },
                "name",
            )
            if existing:
                skipped += 1
                continue

            amount = resolve_category_amount(cat, member, period_start)
            if not amount:
                skipped += 1
                continue

            grace_days = int(cat.get("grace_days") or 0)
            due_date = period_start
            grace_end = add_days(due_date, grace_days) if grace_days else due_date

            ob = frappe.get_doc(
                {
                    "doctype": "Chama Contribution Obligation",
                    "chama": chama,
                    "member": member.name,
                    "cycle": cycle_name,
                    "contribution_category": cat.name,
                    "amount_due": amount,
                    "amount_paid": 0,
                    "amount_waived": 0,
                    "due_date": str(due_date),
                    "grace_end_date": str(grace_end),
                    "status": "Pending",
                    "source_type": "Scheduled",
                }
            )
            ob.insert(ignore_permissions=True)
            created += 1

    frappe.db.commit()
    return {"created": created, "skipped": skipped}


def generate_due_cycles_for_today():
    """
    Daily scheduler entry point.

    Generates cycles and obligations for all Active Chamas where today falls
    within a period that does not yet have a Generated cycle.

    Currently supports Monthly frequency only.
    """
    target = getdate(nowdate())
    first_of_month = target.replace(day=1)
    import calendar
    last_day = calendar.monthrange(target.year, target.month)[1]
    last_of_month = target.replace(day=last_day)

    active_chamas = frappe.get_all(
        "Chama",
        filters={"status": ("in", list(CYCLE_GENERATING_CHAMA_STATUSES))},
        fields=["name"],
    )

    summary = []
    for ch in active_chamas:
        chama = ch.name
        has_categories = frappe.db.count(
            "Chama Contribution Category",
            {"chama": chama, "active": 1, "frequency": "Monthly"},
        )
        if not has_categories:
            continue

        cycle_name, was_created = create_cycle(
            chama=chama,
            period_start=first_of_month,
            period_end=last_of_month,
            frequency="Monthly",
        )
        if was_created:
            result = generate_obligations_for_cycle(cycle_name)
            summary.append({"chama": chama, "cycle": cycle_name, **result})
            frappe.logger().info(
                f"Cycle {cycle_name} created for {chama}: {result['created']} obligations"
            )

    return summary
