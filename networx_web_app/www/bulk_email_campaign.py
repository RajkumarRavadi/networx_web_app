import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	if "System Manager" not in frappe.get_roles():
		frappe.local.flags.redirect_location = "/dashboard"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = True
	context.user = frappe.session.user
	context.is_guest = False
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.user_fullname = frappe.utils.get_fullname(frappe.session.user)
	context.max_recipients = 100

	return context
