import frappe
from frappe.utils import get_url

from networx_web_app.networx_web_app.doctype.user_profile.user_profile import (
	get_public_profile,
)


def get_context(context):
	slug = (frappe.form_dict.get("slug") or "").strip().lower()

	if not slug:
		frappe.local.flags.redirect_location = "/"
		raise frappe.Redirect

	try:
		profile = get_public_profile(slug)
	except frappe.DoesNotExistError:
		frappe.local.flags.redirect_location = "/404"
		raise frappe.Redirect

	context.profile = profile
	context.slug = slug
	context.share_url = f"/profiles/{slug}"
	context.full_share_url = get_url(context.share_url)
	context.page_title = f"{profile.get('full_name') or 'Profile'} | Networx"
	context.no_cache = 0
	context.show_sidebar = False
	context.primary_contact = next(
		(
			row
			for row in (profile.get("contact_info_details") or [])
			if row.get("contact_type") and row.get("contact_value")
		),
		None,
	)

	return context

