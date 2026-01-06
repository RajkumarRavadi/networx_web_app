# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


class UserOTP(Document):
	def is_expired(self):
		"""Check if OTP has expired"""
		if not self.expires_at:
			return True
		return get_datetime(self.expires_at) < now_datetime()

	def is_valid(self):
		"""Check if OTP is valid (not expired and not used)"""
		return not self.is_expired() and not self.is_used

	def mark_as_used(self):
		"""Mark OTP as used after successful verification"""
		self.is_used = 1
		self.save(ignore_permissions=True)
		frappe.db.commit()

	@staticmethod
	def cleanup_expired_otps():
		"""Static method to clean up expired OTPs"""
		expired_otps = frappe.get_all(
			"User OTP",
			filters={
				"expires_at": ["<", now_datetime()],
				"is_used": 0
			},
			pluck="name"
		)
		
		if expired_otps:
			for otp_name in expired_otps:
				frappe.delete_doc("User OTP", otp_name, ignore_permissions=True, force=1)
			
			frappe.db.commit()
			frappe.logger().info(f"Cleaned up {len(expired_otps)} expired OTPs")
