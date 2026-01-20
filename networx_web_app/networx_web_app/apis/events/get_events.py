# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now_datetime, get_datetime
from datetime import timedelta


@frappe.whitelist(allow_guest=True)
def get_events(filters=None, limit=20, offset=0, search_term=None, view_type='upcoming'):
	"""
	Get paginated events with filters
	
	Args:
		filters: JSON string or dict with filters (event_type, location_type, tags, date_range, institute)
		limit: Number of events per page
		offset: Offset for pagination
		search_term: Search in event_name, description, organizer
		view_type: 'upcoming', 'past', 'all', 'my_registrations'
	
	Returns:
		{
			events: [],
			total_count: int,
			has_more: bool,
			limit: int,
			offset: int
		}
	"""
	try:
		limit = int(limit)
		offset = int(offset)
	except (ValueError, TypeError):
		limit = 20
		offset = 0

	# Parse filters if passed as JSON string
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except:
			filters = {}
	
	if not filters:
		filters = {}

	# Base filters - only show published events
	base_filters = {
		"event_status": "Published"
	}

	# Apply view_type filter
	now = now_datetime()
	if view_type == 'upcoming':
		base_filters["event_date"] = [">=", now]
	elif view_type == 'past':
		base_filters["event_date"] = ["<", now]
	# 'all' doesn't add date filter

	# Handle my_registrations view
	if view_type == 'my_registrations':
		user = frappe.session.user
		if user == "Guest":
			return {
				"events": [],
				"total_count": 0,
				"has_more": False,
				"limit": limit,
				"offset": offset
			}
		
		# Get event IDs from user's registrations
		registrations = frappe.db.get_all(
			"Event Registration",
			filters={
				"user": user,
				"registration_status": ["!=", "Cancelled"]
			},
			fields=["event"],
			pluck="event"
		)
		
		if not registrations:
			return {
				"events": [],
				"total_count": 0,
				"has_more": False,
				"limit": limit,
				"offset": offset
			}
		
		base_filters["name"] = ["in", registrations]

	# Merge user filters
	for key, value in filters.items():
		if value:
			if key == "event_type":
				base_filters["event_type"] = value
			elif key == "location_type":
				base_filters["location_type"] = value
			elif key == "institute":
				base_filters["institute"] = value
			elif key == "tags":
				# Tags are comma-separated, search in tags field
				if isinstance(value, str):
					tag_list = [tag.strip() for tag in value.split(",")]
					# Use OR condition for tags
					base_filters["tags"] = ["like", f"%{tag_list[0]}%"]
			elif key == "date_range":
				# date_range can be: 'this_week', 'this_month', 'next_month', or custom dates
				if value == "this_week":
					week_start = now - timedelta(days=now.weekday())
					week_end = week_start + timedelta(days=7)
					base_filters["event_date"] = [">=", week_start]
					base_filters["event_date"] = ["<", week_end]
				elif value == "this_month":
					month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
					next_month = month_start + timedelta(days=32)
					month_end = next_month.replace(day=1) - timedelta(days=1)
					base_filters["event_date"] = [">=", month_start]
					base_filters["event_date"] = ["<=", month_end]
				elif value == "next_month":
					next_month_start = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
					next_next_month = next_month_start + timedelta(days=32)
					next_month_end = next_next_month.replace(day=1) - timedelta(days=1)
					base_filters["event_date"] = [">=", next_month_start]
					base_filters["event_date"] = ["<=", next_month_end]

	# Build search conditions
	search_conditions = []
	if search_term:
		search_conditions.append(
			f"(`event_name` LIKE %(search)s OR `description` LIKE %(search)s OR `organizer_name` LIKE %(search)s)"
		)

	# Get total count
	count_filters = base_filters.copy()
	where_clause = " AND ".join([f"`{k}` = %({k})s" for k in count_filters.keys() if not isinstance(count_filters[k], list)])
	
	# Handle list filters (for date ranges)
	for key, value in count_filters.items():
		if isinstance(value, list) and len(value) == 2:
			operator = value[0]
			val = value[1]
			if operator == ">=":
				where_clause += f" AND `{key}` >= %({key}_val)s"
			elif operator == "<":
				where_clause += f" AND `{key}` < %({key}_val)s"
			elif operator == "<=":
				where_clause += f" AND `{key}` <= %({key}_val)s"
			elif operator == "in":
				placeholders = ",".join([f"%({key}_{i})s" for i in range(len(val))])
				where_clause += f" AND `{key}` IN ({placeholders})"

	if search_conditions:
		where_clause += " AND " + " AND ".join(search_conditions)

	# Prepare values for count query
	count_values = {}
	for key, value in count_filters.items():
		if isinstance(value, list) and len(value) == 2:
			operator = value[0]
			val = value[1]
			if operator in [">=", "<", "<="]:
				count_values[f"{key}_val"] = val
			elif operator == "in":
				for i, v in enumerate(val):
					count_values[f"{key}_{i}"] = v
		elif not isinstance(value, list):
			count_values[key] = value

	if search_term:
		count_values["search"] = f"%{search_term}%"

	# Get count
	total_count = frappe.db.count("Networx Event", base_filters)
	if search_term:
		# Re-count with search
		events_with_search = frappe.db.get_all(
			"Networx Event",
			filters=base_filters,
			or_filters={
				"event_name": ["like", f"%{search_term}%"],
				"description": ["like", f"%{search_term}%"],
				"organizer_name": ["like", f"%{search_term}%"]
			},
			limit_page_length=None
		)
		total_count = len(events_with_search)

	# Get events
	events = frappe.db.get_all(
		"Networx Event",
		filters=base_filters,
		or_filters={
			"event_name": ["like", f"%{search_term}%"],
			"description": ["like", f"%{search_term}%"],
			"organizer_name": ["like", f"%{search_term}%"]
		} if search_term else None,
		fields=[
			"name", "event_name", "event_type", "event_status", "is_featured",
			"event_date", "end_date", "timezone", "location", "location_type",
			"venue_address", "online_meeting_link", "event_banner",
			"registration_enabled", "registration_type", "registration_deadline",
			"max_capacity", "waitlist_enabled", "registration_link",
			"organizer_name", "tags", "target_audience", "institute",
			"is_free", "registration_fee", "currency",
			"total_registrations", "total_attendees", "total_waitlist"
		],
		order_by="event_date ASC" if view_type == 'upcoming' else "event_date DESC",
		limit=limit,
		start=offset
	)

	# Add registration status for logged-in users
	user = frappe.session.user
	if user != "Guest" and view_type != 'my_registrations':
		for event in events:
			registration = frappe.db.get_value(
				"Event Registration",
				{
					"event": event.name,
					"user": user,
					"registration_status": ["!=", "Cancelled"]
				},
				["name", "registration_status", "waitlist_position"],
				as_dict=True
			)
			if registration:
				event["user_registration"] = {
					"registration_id": registration.name,
					"status": registration.registration_status,
					"waitlist_position": registration.waitlist_position or 0
				}
			else:
				event["user_registration"] = None

	# Calculate capacity status
	for event in events:
		if event.max_capacity and event.max_capacity > 0:
			available = event.max_capacity - (event.total_registrations or 0)
			event["capacity_status"] = "full" if available <= 0 else "available"
			event["available_spots"] = max(0, available)
		else:
			event["capacity_status"] = "unlimited"
			event["available_spots"] = None

	return {
		"events": events,
		"total_count": total_count,
		"has_more": (offset + limit) < total_count,
		"limit": limit,
		"offset": offset
	}

