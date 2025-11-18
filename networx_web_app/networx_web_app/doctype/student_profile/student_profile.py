# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentProfile(Document):
	def before_save(self):
		# Auto-populate full name from user if not provided
		if not self.full_name and self.user:
			user = frappe.get_doc("User", self.user)
			self.full_name = user.full_name or user.email



