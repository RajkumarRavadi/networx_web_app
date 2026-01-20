# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, get_datetime


@frappe.whitelist(allow_guest=True)
def get_event_detail(event_id):
	"""
	Get full event details including:
	- Event info
	- Registration stats (if user has permission)
	- User's registration status (if logged in)
	- Available resources
	- Related events
	
	Args:
		event_id: Name/ID of the event
	
	Returns:
		Event details dict with all information
	"""
	if not event_id:
		frappe.throw("Event ID is required")

	# Get event document
	try:
		event = frappe.get_doc("Networx Event", event_id)
	except frappe.DoesNotExistError:
		frappe.throw("Event not found", frappe.DoesNotExistError)

	# Only show published events to guests
	user = frappe.session.user
	if user == "Guest" and event.event_status != "Published":
		frappe.throw("Event not found", frappe.DoesNotExistError)

	# Build event data
	event_data = {
		"name": event.name,
		"event_name": event.event_name,
		"event_type": event.event_type,
		"event_status": event.event_status,
		"is_featured": event.is_featured,
		"event_date": event.event_date,
		"end_date": event.end_date,
		"timezone": event.timezone or "UTC",
		"location": event.location,
		"location_type": event.location_type,
		"venue_address": event.venue_address,
		"online_meeting_link": event.online_meeting_link,
		"event_banner": event.event_banner,
		"description": event.description,
		"registration_enabled": event.registration_enabled,
		"registration_type": event.registration_type,
		"registration_deadline": event.registration_deadline,
		"registration_link": event.registration_link,
		"max_capacity": event.max_capacity,
		"waitlist_enabled": event.waitlist_enabled,
		"waitlist_capacity": event.waitlist_capacity,
		"require_approval": event.require_approval,
		"auto_confirm": event.auto_confirm,
		"organizer_name": event.organizer_name,
		"organizer_email": event.organizer_email,
		"organizer_phone": event.organizer_phone,
		"tags": event.tags,
		"target_audience": event.target_audience,
		"institute": event.institute,
		"is_free": event.is_free,
		"registration_fee": event.registration_fee,
		"currency": event.currency,
		"total_registrations": event.total_registrations or 0,
		"total_attendees": event.total_attendees or 0,
		"total_waitlist": event.total_waitlist or 0
	}

	# Calculate capacity status
	if event.max_capacity and event.max_capacity > 0:
		available = event.max_capacity - (event.total_registrations or 0)
		event_data["capacity_status"] = "full" if available <= 0 else "available"
		event_data["available_spots"] = max(0, available)
		event_data["is_full"] = available <= 0
	else:
		event_data["capacity_status"] = "unlimited"
		event_data["available_spots"] = None
		event_data["is_full"] = False

	# Check registration deadline
	now = now_datetime()
	if event.registration_deadline:
		deadline = get_datetime(event.registration_deadline)
		event_data["registration_closed"] = deadline < now
	else:
		event_data["registration_closed"] = False

	# Get user's registration status (if logged in)
	event_data["user_registration"] = None
	if user != "Guest":
		registration = frappe.db.get_value(
			"Event Registration",
			{
				"event": event.name,
				"user": user,
				"registration_status": ["!=", "Cancelled"]
			},
			["name", "registration_status", "waitlist_position", "registration_date", "check_in_time"],
			as_dict=True
		)
		if registration:
			event_data["user_registration"] = {
				"registration_id": registration.name,
				"status": registration.registration_status,
				"waitlist_position": registration.waitlist_position or 0,
				"registration_date": registration.registration_date,
				"checked_in": bool(registration.check_in_time)
			}

	# Get resources (only available ones)
	resources = []
	now = now_datetime()
	event_end = get_datetime(event.end_date) if event.end_date else get_datetime(event.event_date)
	
	for resource in event.resources or []:
		# Check if resource is available
		is_available = True
		if resource.available_after_event:
			if event_end and event_end > now:
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
	
	event_data["resources"] = resources

	# Get related events (same type, different event, upcoming)
	related_events = frappe.db.get_all(
		"Networx Event",
		filters={
			"event_type": event.event_type,
			"event_status": "Published",
			"name": ["!=", event.name],
			"event_date": [">=", now]
		},
		fields=["name", "event_name", "event_date", "location", "event_banner"],
		order_by="event_date ASC",
		limit=3
	)
	event_data["related_events"] = related_events

	# Get institute info if linked
	if event.institute:
		institute_info = frappe.db.get_value(
			"Institute Profile",
			event.institute,
			["name", "institute_name", "logo"],
			as_dict=True
		)
		if institute_info:
			event_data["institute_info"] = institute_info

	return event_data

