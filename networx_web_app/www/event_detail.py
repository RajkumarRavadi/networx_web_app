import frappe

def get_context(context):
	# Allow public access - no authentication required
	context.no_cache = 1
	context.show_sidebar = False
	
	# Get event_id from route
	event_id = frappe.form_dict.get('event_id')
	context.event_id = event_id
	
	# Pass user info to template
	context.user = frappe.session.user if frappe.session.user != "Guest" else None
	context.is_guest = frappe.session.user == "Guest"
	
	return context

