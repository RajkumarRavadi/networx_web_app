# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, get_datetime


@frappe.whitelist()
def get_my_registrations(status=None):
	"""
	Get current user's event registrations
	Filter by status: 'upcoming', 'past', 'waitlisted', 'all'
	
	Args:
		status: Filter status ('upcoming', 'past', 'waitlisted', 'all', None)
	
	Returns:
		List of registrations with event details
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login to view your registrations", frappe.PermissionError)

	now = now_datetime()

	# Base filters
	base_filters = {
		"user": user,
		"registration_status": ["!=", "Cancelled"]
	}

	# Get registrations
	registrations = frappe.db.get_all(
		"Event Registration",
		filters=base_filters,
		fields=[
			"name", "event", "registration_status", "registration_date",
			"waitlist_position", "check_in_time", "registration_type"
		],
		order_by="registration_date DESC"
	)

	# Get event details for each registration
	result = []
	for reg in registrations:
		try:
			event = frappe.get_doc("Networx Event", reg.event)
		except frappe.DoesNotExistError:
			continue

		event_date = get_datetime(event.event_date)
		is_upcoming = event_date > now
		is_past = event_date < now
		is_waitlisted = reg.waitlist_position > 0

		# Apply status filter
		if status:
			if status == "upcoming" and not is_upcoming:
				continue
			elif status == "past" and not is_past:
				continue
			elif status == "waitlisted" and not is_waitlisted:
				continue
			# 'all' doesn't filter

		# Build registration data
		reg_data = {
			"registration_id": reg.name,
			"registration_status": reg.registration_status,
			"registration_date": reg.registration_date,
			"waitlist_position": reg.waitlist_position or 0,
			"is_waitlisted": is_waitlisted,
			"checked_in": bool(reg.check_in_time),
			"check_in_time": reg.check_in_time,
			"registration_type": reg.registration_type,
			"event": {
				"name": event.name,
				"event_name": event.event_name,
				"event_type": event.event_type,
				"event_date": event.event_date,
				"end_date": event.end_date,
				"location": event.location,
				"location_type": event.location_type,
				"venue_address": event.venue_address,
				"online_meeting_link": event.online_meeting_link,
				"event_banner": event.event_banner,
				"organizer_name": event.organizer_name,
				"organizer_email": event.organizer_email,
				"organizer_phone": event.organizer_phone,
				"description": event.description,
				"is_upcoming": is_upcoming,
				"is_past": is_past,
				"registration_deadline": event.registration_deadline,
				"registration_link": event.registration_link
			}
		}

		# Get resources if event is past
		if is_past:
			resources = []
			event_end = get_datetime(event.end_date) if event.end_date else event_date
			
			for resource in event.resources or []:
				is_available = True
				if resource.available_after_event:
					if event_end > now:
						is_available = False
				
				if resource.release_date:
					release = get_datetime(resource.release_date)
					if release > now:
						is_available = False
				
				if is_available:
					resources.append({
						"name": resource.name,
						"resource_name": resource.resource_name,
						"resource_type": resource.resource_type,
						"resource_file": resource.resource_file,
						"resource_url": resource.resource_url
					})
			
			reg_data["event"]["resources"] = resources

		result.append(reg_data)

	# Sort by event date
	result.sort(key=lambda x: get_datetime(x["event"]["event_date"]), reverse=status != "upcoming")

	return result

