# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UserProfileEducation(Document):
	def validate(self):
		# Auto-fill institution_name from institute Link if institute is selected
		if self.institute and not self.institution_name:
			institute_name = frappe.db.get_value("Institute Profile", self.institute, "institute_name")
			if institute_name:
				self.institution_name = institute_name
		
		# Ensure at least one of institute or institution_name is provided
		if not self.institute and not self.institution_name:
			frappe.throw("Please select an institute or enter institution name")

