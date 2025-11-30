import frappe
from frappe.utils import now_datetime

# 1. @frappe.whitelist(): This tells Frappe "Allow this function to be called from the Internet/Browser".
# allow_guest=True means "You don't need to login to call this" (Useful for public kiosks).
@frappe.whitelist(allow_guest=True)
def create_visitor_log(visitor_name, purpose):
    """
    API Endpoint to create a log.
    Usage: POST to /api/method/campus_gate.api.create_visitor_log
    """
    
    # 2. Validation: Check if data is missing
    if not visitor_name:
        return {"status": "error", "message": "Visitor Name is required"}

    try:
        # 3. Create the Document (The "INSERT INTO" equivalent)
        # We use frappe.get_doc({...}) to prepare the data
        new_log = frappe.get_doc({
            "doctype": "Visitor Log",      # Which table?
            "visitor_name": visitor_name,  # Field: Value
            "purpose": purpose,
            "entry_time": now_datetime(),  # Set time to NOW
            "status": "In"
        })

        # 4. Insert into Database
        # ignore_permissions=True is vital for APIs where the user might be a Guest
        new_log.insert(ignore_permissions=True)

        # 5. Return Success
        return {
            "status": "success",
            "message": "Entry Logged",
            "log_id": new_log.name
        }

    except Exception as e:
        # 6. Error Handling: Log the error in Frappe's backend log so we can debug later
        frappe.log_error(f"Visitor API Error: {str(e)}")
        return {"status": "failed", "error": str(e)}
    
def check_banned_visitors(doc, method):
    """
    Hook to check if the visitor is banned during validation of Visitor Log.
    """
    if doc.visitor_name:
        doc.visitor_name = doc.visitor_name.title()
    if doc.visitor_name.lower() == "voldemort" and doc.purpose.lower() == "dark magic":
        frappe.throw("This visitor is banned from entering the campus.")