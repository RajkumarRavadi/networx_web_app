# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobApplication(Document):
	def validate(self):
		# Ensure a student can't apply to the same job twice
		existing = frappe.db.exists(
			"Job Application",
			{
				"student_profile": self.student_profile,
				"job_opening": self.job_opening,
				"name": ["!=", self.name]
			}
		)
		if existing:
			frappe.throw("You have already applied for this job")



