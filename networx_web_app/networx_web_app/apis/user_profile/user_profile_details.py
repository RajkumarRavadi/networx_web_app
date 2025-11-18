import frappe

@frappe.whitelist()
def get_user_profile_details(user=None):
    # get complete details of the user profile 
    if not user:
        user = frappe.session.user
    
    if user == "Guest":
        frappe.throw("Please login to view profile")
    
    if not frappe.db.exists("User Profile", user):
        frappe.throw(f"User Profile not found for user: {user}")
    
    user_profile = frappe.get_doc("User Profile", user)
    return user_profile.as_dict()