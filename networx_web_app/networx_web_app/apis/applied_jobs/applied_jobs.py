import json
from typing import Dict, Tuple

import frappe
from frappe.utils import cint

APPLIED_JOBS_FIELDS = [
	"name",
	"job_application",
	"job_opening",
	"job_title_snapshot",
	"company_name_snapshot",
	"employment_type",
	"job_location",
	"application_date",
	"current_stage",
	"stage_updated_on",
	"application_source",
	"application_medium",
	"channel_tags",
	"total_applications_by_user",
	"rolling_30_day_applications",
	"total_applications_for_job",
	"is_repeat_application",
	"is_duplicate_flagged",
	"status_reason",
	"notes",
]


@frappe.whitelist()
def get_user_applied_jobs(user: str | None = None, limit: int = 20, offset: int = 0, filters=None, search_term: str | None = None):
	user = _resolve_user(user)
	limit = _safe_positive_int(limit, 20)
	offset = max(_safe_positive_int(offset, 0), 0)
	parsed_filters = _coerce_filters(filters)

	where_clause, params = _build_conditions(user, parsed_filters, search_term)
	rows = frappe.db.sql(
		f"""
		SELECT {", ".join(f"`{field}`" for field in APPLIED_JOBS_FIELDS)}
		FROM `tabApplied Jobs`
		WHERE {where_clause}
		ORDER BY `application_date` DESC
		LIMIT %(limit)s OFFSET %(offset)s
		""",
		{**params, "limit": limit, "offset": offset},
		as_dict=True,
	)

	total_count = frappe.db.sql(
		f"SELECT COUNT(*) AS total FROM `tabApplied Jobs` WHERE {where_clause}",
		params,
		as_dict=True,
	)[0].total

	return {
		"records": rows,
		"total_count": total_count,
		"limit": limit,
		"offset": offset,
	}


@frappe.whitelist()
def get_applied_jobs_insights(user: str | None = None):
	user = _resolve_user(user)
	base_filters = {"user_account": user}
	total = frappe.db.count("Applied Jobs", base_filters)

	last_application_date = frappe.db.get_value(
		"Applied Jobs",
		base_filters,
		"application_date",
		order_by="application_date desc",
	)

	stage_breakdown = _group_counts("current_stage", base_filters)
	source_breakdown = _group_counts("application_source", base_filters)

	recent_updates = frappe.get_all(
		"Applied Jobs",
		fields=[
			"name",
			"job_title_snapshot",
			"company_name_snapshot",
			"current_stage",
			"stage_updated_on",
			"status_reason",
		],
		filters=base_filters,
		limit_page_length=5,
		order_by="stage_updated_on desc",
	)

	return {
		"total_applications": total,
		"stage_breakdown": stage_breakdown,
		"source_breakdown": source_breakdown,
		"last_application_date": last_application_date,
		"recent_updates": recent_updates,
	}


def _build_conditions(user: str, parsed_filters: Dict, search_term: str | None) -> Tuple[str, Dict]:
	conditions = ["`user_account` = %(user)s"]
	params = {"user": user}

	stage = parsed_filters.get("current_stage")
	if stage:
		conditions.append("`current_stage` = %(current_stage)s")
		params["current_stage"] = stage

	source = parsed_filters.get("application_source")
	if source:
		conditions.append("`application_source` = %(application_source)s")
		params["application_source"] = source

	medium = parsed_filters.get("application_medium")
	if medium:
		conditions.append("`application_medium` = %(application_medium)s")
		params["application_medium"] = medium

	channel_tag = parsed_filters.get("channel_tag")
	if channel_tag:
		conditions.append("`channel_tags` LIKE %(channel_tag)s")
		params["channel_tag"] = f"%{channel_tag}%"

	start_date = parsed_filters.get("application_date_from")
	if start_date:
		conditions.append("`application_date` >= %(application_date_from)s")
		params["application_date_from"] = start_date

	end_date = parsed_filters.get("application_date_to")
	if end_date:
		conditions.append("`application_date` <= %(application_date_to)s")
		params["application_date_to"] = end_date

	if search_term:
		conditions.append(
			"(`job_title_snapshot` LIKE %(search)s OR `company_name_snapshot` LIKE %(search)s)"
		)
		params["search"] = f"%{search_term}%"

	return " AND ".join(conditions), params


def _group_counts(fieldname: str, filters: Dict) -> Dict[str, int]:
	if not filters:
		return {}
	conditions = []
	params = {}
	for key, value in filters.items():
		conditions.append(f"`{key}` = %({key})s")
		params[key] = value
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	rows = frappe.db.sql(
		f"""
		SELECT `{fieldname}` AS label, COUNT(*) AS total
		FROM `tabApplied Jobs`
		WHERE {where_clause}
		GROUP BY `{fieldname}`
		""",
		params,
		as_dict=True,
	)
	return {row.label or "Unknown": row.total for row in rows}


def _resolve_user(user: str | None) -> str:
	session_user = frappe.session.user
	if user and user != session_user and session_user != "Administrator":
		frappe.only_for(("System Manager",))
	resolved = user or session_user
	if not resolved or resolved == "Guest":
		frappe.throw("A valid user is required to access applied jobs data.")
	return resolved


def _coerce_filters(raw_filters) -> Dict:
	if not raw_filters:
		return {}
	if isinstance(raw_filters, dict):
		return raw_filters
	if isinstance(raw_filters, str):
		try:
			return json.loads(raw_filters)
		except json.JSONDecodeError:
			return {}
	return {}


def _safe_positive_int(value, default: int) -> int:
	try:
		num = cint(value)
		return num if num >= 0 else default
	except Exception:
		return default


