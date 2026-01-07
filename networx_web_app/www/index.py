import frappe

def get_context(context):
	# Redirect logged-in users to dashboard
	# Only guests should see the landing page
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/dashboard"
		raise frappe.Redirect
	
	# Allow guest access to landing page
	context.no_cache = 1
	context.show_sidebar = False
	
	# Pass user info to template (similar to jobs.py)
	context.user = None
	context.is_guest = True
	
	return context

