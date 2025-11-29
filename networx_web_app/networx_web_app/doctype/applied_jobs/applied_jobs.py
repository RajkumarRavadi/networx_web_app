# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

from __future__ import annotations

from typing import Optional

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, now_datetime, nowdate

STAGE_MAP = {
	"Applied": "Applied",
	"Under Review": "Screening",
	"Rejected": "Rejected",
	"Accepted": "Hired",
}


class AppliedJobs(Document):
	def validate(self):
		self._set_defaults()
		self._populate_user_details()
		self._populate_job_snapshot()
		self._update_metrics()
		self._flag_duplicates()

	def before_save(self):
		self._capture_stage_history()

	def _set_defaults(self):
		if not self.application_date:
			self.application_date = nowdate()
		if not self.current_stage:
			self.current_stage = "Applied"
		if not self.stage_updated_on:
			self.stage_updated_on = now_datetime()

	def _populate_user_details(self):
		if not self.user_profile:
			return
		profile = frappe.db.get_value(
			"Student Profile",
			self.user_profile,
			["user", "full_name"],
			as_dict=True,
		)
		if not profile:
			return
		self.user_account = profile.user
		self.user_full_name = profile.full_name

	def _populate_job_snapshot(self):
		if not self.job_opening:
			return
		job = frappe.db.get_value(
			"Job Opening",
			self.job_opening,
			["job_title", "company_name", "job_type", "location"],
			as_dict=True,
		)
		if not job:
			return
		self.job_title_snapshot = job.job_title
		self.company_name_snapshot = job.company_name
		self.employment_type = job.job_type
		self.job_location = job.location

	def _update_metrics(self):
		if not self.user_profile:
			return
		user_filters = {"student_profile": self.user_profile}
		self.total_applications_by_user = frappe.db.count("Job Application", user_filters)

		cutoff_date = add_days(nowdate(), -30)
		rolling_filters = user_filters.copy()
		rolling_filters["application_date"] = (">=", cutoff_date)
		self.rolling_30_day_applications = frappe.db.count("Job Application", rolling_filters)
		self.is_repeat_application = self.total_applications_by_user > 1

		if self.job_opening:
			self.total_applications_for_job = frappe.db.count(
				"Job Application", {"job_opening": self.job_opening}
			)

	def _flag_duplicates(self):
		if not self.user_profile or not self.job_opening:
			self.is_duplicate_flagged = 0
			return
		filters = {
			"user_profile": self.user_profile,
			"job_opening": self.job_opening,
		}
		if self.name:
			filters["name"] = ["!=", self.name]
		self.is_duplicate_flagged = 1 if frappe.db.exists("Applied Jobs", filters) else 0

	def _capture_stage_history(self):
		if not self.current_stage:
			return
		previous_stage = None
		if not self.is_new():
			previous_stage = frappe.db.get_value(self.doctype, self.name, "current_stage")
		if previous_stage == self.current_stage:
			return
		self.stage_updated_on = now_datetime()
		self.append(
			"status_history",
			{
				"status_timestamp": self.stage_updated_on,
				"from_stage": previous_stage or "Not Set",
				"to_stage": self.current_stage,
				"changed_by": frappe.session.user,
				"notes": self.status_reason,
			},
		)


def upsert_from_job_application(job_application: Document | str):
	doc = _coerce_job_application(job_application)
	if not doc or not doc.student_profile or not doc.job_opening:
		return

	applied_job_name = frappe.db.exists("Applied Jobs", {"job_application": doc.name})
	applied_job = (
		frappe.get_doc("Applied Jobs", applied_job_name)
		if applied_job_name
		else frappe.new_doc("Applied Jobs")
	)

	applied_job.job_application = doc.name
	applied_job.user_profile = doc.student_profile
	applied_job.job_opening = doc.job_opening
	applied_job.application_date = doc.application_date or nowdate()
	applied_job.current_stage = STAGE_MAP.get(doc.status, "Applied")
	applied_job.status_reason = getattr(doc, "status_reason", None)
	if getattr(doc, "cover_letter", None) and not applied_job.notes:
		applied_job.notes = doc.cover_letter

	applied_job.save(ignore_permissions=True)


def _coerce_job_application(job_application: Document | str) -> Optional[Document]:
	if isinstance(job_application, Document):
		return job_application
	if isinstance(job_application, str):
		return frappe.get_doc("Job Application", job_application)
	return None


