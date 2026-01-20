# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


class NetworxEvent(Document):
	def validate(self):
		self._validate_dates()
		self._validate_capacity()
		self._validate_registration_settings()
		self._update_analytics()

	def _validate_dates(self):
		"""Validate event dates"""
		if not self.event_date:
			frappe.throw("Event Start Date is required")

		if self.end_date:
			if get_datetime(self.end_date) < get_datetime(self.event_date):
				frappe.throw("Event End Date must be after Event Start Date")

		if self.registration_deadline:
			if get_datetime(self.registration_deadline) > get_datetime(self.event_date):
				frappe.throw("Registration Deadline must be before Event Start Date")

	def _validate_capacity(self):
		"""Validate capacity settings"""
		if self.max_capacity and self.max_capacity < 0:
			frappe.throw("Maximum Capacity cannot be negative")

		if self.waitlist_capacity and self.waitlist_capacity < 0:
			frappe.throw("Waitlist Capacity cannot be negative")

		if self.waitlist_enabled and (not self.max_capacity or self.max_capacity == 0):
			frappe.throw("Waitlist can only be enabled when Maximum Capacity is set")

	def _validate_registration_settings(self):
		"""Validate registration-related settings"""
		if not self.registration_enabled:
			# If registration is disabled, clear related fields
			if self.registration_type:
				self.registration_type = None
			if self.max_capacity:
				self.max_capacity = 0
			if self.waitlist_enabled:
				self.waitlist_enabled = 0

		if self.require_approval and self.auto_confirm:
			# If approval required, auto_confirm should be off
			self.auto_confirm = 0

	def _update_analytics(self):
		"""Update analytics fields based on registrations"""
		if self.is_new():
			# Initialize analytics for new events
			self.total_registrations = 0
			self.total_attendees = 0
			self.total_waitlist = 0
		else:
			# Calculate from Event Registration records
			confirmed_count = frappe.db.count(
				"Event Registration",
				{
					"event": self.name,
					"registration_status": ["in", ["Confirmed", "Attended"]]
				}
			)
			
			waitlist_count = frappe.db.count(
				"Event Registration",
				{
					"event": self.name,
					"registration_status": "Pending",
					"waitlist_position": [">", 0]
				}
			)

			attended_count = frappe.db.count(
				"Event Registration",
				{
					"event": self.name,
					"registration_status": "Attended"
				}
			)

			total_registrations = frappe.db.count(
				"Event Registration",
				{
					"event": self.name,
					"registration_status": ["!=", "Cancelled"]
				}
			)

			self.total_registrations = total_registrations
			self.total_attendees = attended_count
			self.total_waitlist = waitlist_count

	def on_update(self):
		"""Called after document is saved"""
		# Auto-update status based on dates
		if self.event_status != "Cancelled":
			now = now_datetime()
			event_start = get_datetime(self.event_date)
			
			if event_start and event_start < now:
				if self.end_date:
					event_end = get_datetime(self.end_date)
					if event_end and event_end < now:
						if self.event_status != "Completed":
							self.db_set("event_status", "Completed", update_modified=False)
				else:
					# Single day event that has passed
					if self.event_status != "Completed":
						self.db_set("event_status", "Completed", update_modified=False)



