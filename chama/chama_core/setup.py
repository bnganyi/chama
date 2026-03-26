"""
Post-install setup for the Chama app.

Creates required Module Def records so that Frappe recognises all modules
defined in modules.txt and can route DocTypes correctly.
"""

import frappe


def after_install():
    """Create Module Def records for all chama modules."""
    _ensure_module_def("Chama Core", "chama")
    _ensure_module_def("Chama Contributions", "chama")


def _ensure_module_def(module_name, app_name):
    if frappe.db.exists("Module Def", module_name):
        return

    module_def = frappe.get_doc(
        {
            "doctype": "Module Def",
            "module_name": module_name,
            "app_name": app_name,
        }
    )
    module_def.insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.logger().info(f"Created Module Def: {module_name}")
