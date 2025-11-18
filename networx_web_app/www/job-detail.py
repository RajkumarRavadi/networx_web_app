import frappe

def get_context(context):
	# Require authentication
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	
	context.no_cache = 1
	context.show_sidebar = False
	
	# Get job ID from query params
	job_id = frappe.form_dict.get('id')
	if not job_id:
		frappe.throw("Job ID is required")
	
	context.job_id = job_id
	
	return context



