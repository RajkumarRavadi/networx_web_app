import frappe

def get_context(context):
	# Redirect to dashboard if already logged in
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/dashboard"
		raise frappe.Redirect
	
	context.no_cache = 1
	context.show_sidebar = False
	
	return context



