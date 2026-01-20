import frappe

def get_context(context):
	# Require login
	if frappe.session.user == "Guest":
		frappe.throw("Please login to view your events", frappe.PermissionError)
	
	context.no_cache = 1
	context.show_sidebar = False
	
	# Pass user info to template
	context.user = frappe.session.user
	context.is_guest = False
	
	return context

