"""
Standardised API response helpers for all Chama API endpoints.

All whitelisted API methods must use these functions for their return values
to ensure a consistent, predictable response envelope.
"""

import frappe


def success_response(data=None, meta=None):
    """
    Return a standard success envelope.

    Args:
        data (dict | list | None): The payload to return to the caller.
        meta (dict | None): Optional metadata (pagination, totals, etc.).

    Returns:
        dict: {"status": "success", "data": ..., "meta": ..., "errors": []}
    """
    return {
        "status": "success",
        "data": data or {},
        "meta": meta or {},
        "errors": [],
    }


def error_response(error_code, message, details=None, http_status_code=None):
    """
    Return a standard error envelope and optionally set the HTTP status code.

    Args:
        error_code (str): A machine-readable error code (e.g. "UNAUTHORIZED", "NOT_FOUND").
        message (str): A human-readable error description.
        details (dict | None): Additional context for the error.
        http_status_code (int | None): If provided, sets the HTTP response status.

    Returns:
        dict: {"status": "error", "data": None, "meta": {}, "errors": [...]}
    """
    if http_status_code:
        frappe.local.response["http_status_code"] = http_status_code

    return {
        "status": "error",
        "data": None,
        "meta": {},
        "errors": [
            {
                "error_code": error_code,
                "message": message,
                "details": details or {},
            }
        ],
    }


def validation_error_response(errors):
    """
    Return a standard validation-error envelope for field-level errors.

    Args:
        errors (list[dict]): Each item must have at least "field" and "message" keys.
            Example: [{"field": "phone", "message": "Phone is required."}]

    Returns:
        dict: {"status": "error", "data": None, "meta": {}, "errors": [...]}
    """
    frappe.local.response["http_status_code"] = 422

    return {
        "status": "error",
        "data": None,
        "meta": {},
        "errors": errors,
    }
