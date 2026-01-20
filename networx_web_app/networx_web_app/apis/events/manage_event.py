# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
import csv
from frappe.utils import now_datetime
from frappe import _


@frappe.whitelist()
def get_event_registrations(event_id, status=None):
	"""
	Get all registrations for an event (admin only)
	
	Args:
		event_id: Event ID/name
		status: Optional filter by registration_status
	
	Returns:
		List of registrations with user details
	"""
	# Check permission
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Permission denied", frappe.PermissionError)

	if not event_id:
		frappe.throw("Event ID is required")

	# Verify event exists
	if not frappe.db.exists("Networx Event", event_id):
		frappe.throw("Event not found")

	# Build filters
	filters = {"event": event_id}
	if status:
		filters["registration_status"] = status

	# Get registrations
	registrations = frappe.db.get_all(
		"Event Registration",
		filters=filters,
		fields=[
			"name", "user", "user_profile", "registration_date",
			"registration_status", "waitlist_position", "check_in_time",
			"cancellation_reason", "notes", "registration_type"
		],
		order_by="registration_date ASC"
	)

	# Enrich with user details
	result = []
	for reg in registrations:
		user_details = frappe.db.get_value(
			"User",
			reg.user,
			["full_name", "email", "name"],
			as_dict=True
		)

		reg_data = {
			"registration_id": reg.name,
			"user": reg.user,
			"user_name": user_details.full_name if user_details else reg.user,
			"user_email": user_details.email if user_details else None,
			"user_profile": reg.user_profile,
			"registration_date": reg.registration_date,
			"registration_status": reg.registration_status,
			"waitlist_position": reg.waitlist_position or 0,
			"check_in_time": reg.check_in_time,
			"checked_in": bool(reg.check_in_time),
			"cancellation_reason": reg.cancellation_reason,
			"notes": reg.notes,
			"registration_type": reg.registration_type
		}

		result.append(reg_data)

	return result


@frappe.whitelist()
def update_registration_status(registration_id, status):
	"""
	Update registration status (admin only)
	
	Args:
		registration_id: Registration ID/name
		status: New status (Pending, Confirmed, Cancelled, Attended, No Show)
	
	Returns:
		Success message
	"""
	# Check permission
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Permission denied", frappe.PermissionError)

	if not registration_id or not status:
		frappe.throw("Registration ID and status are required")

	valid_statuses = ["Pending", "Confirmed", "Cancelled", "Attended", "No Show"]
	if status not in valid_statuses:
		frappe.throw(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

	# Get registration
	try:
		registration = frappe.get_doc("Event Registration", registration_id)
	except frappe.DoesNotExistError:
		frappe.throw("Registration not found")

	old_status = registration.registration_status
	registration.registration_status = status

	# Clear waitlist position if confirmed
	if status == "Confirmed" and registration.waitlist_position > 0:
		registration.waitlist_position = 0

	registration.save(ignore_permissions=True)

	# Update event analytics
	event = frappe.get_doc("Networx Event", registration.event)
	event._update_analytics()
	event.save(ignore_permissions=True)

	return {
		"success": True,
		"message": f"Registration status updated from {old_status} to {status}"
	}


@frappe.whitelist()
def check_in_attendee(registration_id):
	"""
	Mark attendee as checked in
	
	Args:
		registration_id: Registration ID/name
	
	Returns:
		Success message
	"""
	# Check permission
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Permission denied", frappe.PermissionError)

	if not registration_id:
		frappe.throw("Registration ID is required")

	# Get registration
	try:
		registration = frappe.get_doc("Event Registration", registration_id)
	except frappe.DoesNotExistError:
		frappe.throw("Registration not found")

	# Check if already checked in
	if registration.check_in_time:
		frappe.throw("Attendee is already checked in")

	# Update registration
	registration.check_in_time = now_datetime()
	if registration.registration_status != "Attended":
		registration.registration_status = "Attended"
	registration.save(ignore_permissions=True)

	# Update event analytics
	event = frappe.get_doc("Networx Event", registration.event)
	event._update_analytics()
	event.save(ignore_permissions=True)

	return {
		"success": True,
		"message": "Attendee checked in successfully",
		"check_in_time": registration.check_in_time
	}


@frappe.whitelist()
def export_event_registrations(event_id, format='csv'):
	"""
	Export registrations to CSV/Excel
	
	Args:
		event_id: Event ID/name
		format: 'csv' or 'excel' (currently only CSV supported)
	
	Returns:
		CSV data as string
	"""
	# Check permission
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Permission denied", frappe.PermissionError)

	if not event_id:
		frappe.throw("Event ID is required")

	# Get event
	try:
		event = frappe.get_doc("Networx Event", event_id)
	except frappe.DoesNotExistError:
		frappe.throw("Event not found")

	# Get registrations
	registrations = frappe.db.get_all(
		"Event Registration",
		filters={"event": event_id},
		fields=[
			"name", "user", "registration_date", "registration_status",
			"waitlist_position", "check_in_time", "registration_type"
		],
		order_by="registration_date ASC"
	)

	# Build CSV
	import io
	output = io.StringIO()
	writer = csv.writer(output)

	# Header
	writer.writerow([
		"Registration ID", "User", "User Name", "User Email",
		"Registration Date", "Status", "Waitlist Position",
		"Check-in Time", "Registration Type"
	])

	# Data rows
	for reg in registrations:
		user_details = frappe.db.get_value(
			"User",
			reg.user,
			["full_name", "email"],
			as_dict=True
		)

		writer.writerow([
			reg.name,
			reg.user,
			user_details.full_name if user_details else "",
			user_details.email if user_details else "",
			reg.registration_date or "",
			reg.registration_status or "",
			reg.waitlist_position or 0,
			reg.check_in_time or "",
			reg.registration_type or ""
		])

	csv_data = output.getvalue()
	output.close()

	return {
		"success": True,
		"data": csv_data,
		"filename": f"{event.event_name}_registrations.csv"
	}

