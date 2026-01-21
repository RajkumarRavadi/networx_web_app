import frappe

def get_context(context):
	# Allow public access - no authentication required
	context.no_cache = 1
	context.show_sidebar = False
	
	# Pass user info to template
	context.user = frappe.session.user if frappe.session.user != "Guest" else None
	context.is_guest = frappe.session.user == "Guest"
	
	# Add CSRF token to context for use in JavaScript
	context.csrf_token = frappe.sessions.get_csrf_token()
	
	return context

