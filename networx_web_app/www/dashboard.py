import frappe

def get_context(context):
	# Require authentication
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	
	context.no_cache = 1
	context.show_sidebar = False
	context.user_fullname = frappe.utils.get_fullname(frappe.session.user)
	
	return context



