"""
Post-install setup for the Chama Contributions module.

Called from chama_core/setup.py after_install().
"""

import frappe


def ensure_module_def():
    """Create the Chama Contributions Module Def record if it does not already exist."""
    if frappe.db.exists("Module Def", "Chama Contributions"):
        return

    module_def = frappe.get_doc(
        {
            "doctype": "Module Def",
            "module_name": "Chama Contributions",
            "app_name": "chama",
        }
    )
    module_def.insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.logger().info("Created Module Def: Chama Contributions")
