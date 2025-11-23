import frappe

def get_context(context):
	# Require authentication
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	
	context.no_cache = 1
	context.show_sidebar = False
	
	# Add CSRF token to context for use in JavaScript
	context.csrf_token = frappe.sessions.get_csrf_token()
	
	return context

