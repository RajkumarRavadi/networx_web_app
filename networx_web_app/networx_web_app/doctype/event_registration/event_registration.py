# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventRegistration(Document):
	def before_insert(self):
		# Auto-link user_profile if not set
		if self.user and not self.user_profile:
			user_profile = frappe.db.get_value("User Profile", {"user": self.user}, "name")
			if user_profile:
				self.user_profile = user_profile

