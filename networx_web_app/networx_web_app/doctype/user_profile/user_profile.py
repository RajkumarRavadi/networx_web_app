# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import re
from datetime import date, datetime
from typing import Dict, List

import frappe
from frappe.model.document import Document
from frappe.utils import cint, random_string, sanitize_html

PUBLIC_CACHE_PREFIX = "user_profile_public::"


class UserProfile(Document):
	def before_save(self):
		self._previous_public_slug = (
			frappe.db.get_value("User Profile", self.name, "public_slug") if not self.is_new() else None
		)
		self._prepare_public_slug()

	def on_update(self):
		cache = frappe.cache()
		for slug in {getattr(self, "_previous_public_slug", None), self.public_slug}:
			if slug:
				cache.delete_value(_cache_key(slug))

	def _prepare_public_slug(self):
		if not cint(self.is_public):
			self.public_slug = None
			return

		slug = self._slugify(self.public_slug or self.full_name or self.user or "")

		if not slug:
			slug = f"profile-{random_string(8).lower()}"

		self.public_slug = self._deduplicate_slug(slug)

	def _deduplicate_slug(self, base_slug: str) -> str:
		slug = base_slug
		counter = 1
		filters = {"public_slug": slug}
		name_filter = self.name or self.user
		if name_filter:
			filters["name"] = ["!=", name_filter]

		while frappe.db.exists("User Profile", filters):
			slug = f"{base_slug}-{counter}"
			filters["public_slug"] = slug
			counter += 1

		return slug

	@staticmethod
	def _slugify(value: str) -> str:
		if not value:
			return ""
		value = value.lower()
		value = re.sub(r"[^a-z0-9]+", "-", value)
		return value.strip("-")


def _cache_key(slug: str) -> str:
	return f"{PUBLIC_CACHE_PREFIX}{slug}"


SAFE_PROFILE_FIELDS = [
	"user",
	"full_name",
	"headline",
	"current_location",
	"industry",
	"profile_summary",
	"profile_image",
	"profile_url",
	"public_slug",
	"modified",
]

PUBLIC_CHILD_FIELD_MAP: Dict[str, List[str]] = {
	"contact_info_details": ["contact_type", "contact_value"],
	"experience": [
		"title",
		"company_name",
		"employment_type",
		"location",
		"start_date",
		"end_date",
		"description",
	],
	"education": [
		"institution_name",
		"degree",
		"field_of_study",
		"start_year",
		"end_year",
		"grade",
		"activities_societies",
		"description",
	],
	"skills": ["skill_name", "endorsement_count"],
	"certifications": [
		"certification_name",
		"issuing_organization",
		"issue_date",
		"expiration_date",
		"credential_id",
		"credential_url",
	],
	"volunteer_experience": [
		"organization",
		"role",
		"cause",
		"start_date",
		"end_date",
		"description",
	],
	"awards": ["title", "issuer", "issue_date", "description"],
}


def _serialize_value(value):
	if isinstance(value, (datetime, date)):
		return value.isoformat()
	return value


def _serialize_public_profile(doc: Document) -> Dict:
	data = {field: _serialize_value(doc.get(field)) for field in SAFE_PROFILE_FIELDS}
	if data.get("profile_summary"):
		data["profile_summary"] = sanitize_html(data["profile_summary"], always_sanitize=True)

	for child_field, allowed_keys in PUBLIC_CHILD_FIELD_MAP.items():
		rows = []
		for row in doc.get(child_field) or []:
			rows.append({key: _serialize_value(row.get(key)) for key in allowed_keys})
		data[child_field] = rows

	data["updated_on"] = _serialize_value(doc.modified)
	return data


@frappe.whitelist(allow_guest=True)
def get_public_profile(slug: str):
	slug = (slug or "").strip().lower()
	if not slug:
		frappe.throw("Profile link is missing.")

	cache = frappe.cache()
	cache_key = _cache_key(slug)
	cached_profile = cache.get_value(cache_key)
	if cached_profile:
		return cached_profile

	profile_name = frappe.db.get_value(
		"User Profile", {"public_slug": slug, "is_public": 1}, "name"
	)
	if not profile_name:
		raise frappe.DoesNotExistError("Public profile not found.")

	doc = frappe.get_doc("User Profile", profile_name)
	public_profile = _serialize_public_profile(doc)
	cache.set_value(cache_key, public_profile, expires_in_sec=300)

	return public_profile

