# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now_datetime, get_datetime
from frappe import _


@frappe.whitelist()
def register_for_event(event_id, registration_data=None):
	"""
	Register user for event
	- Check capacity
	- Add to waitlist if full
	- Send confirmation email
	- Return registration status
	
	Args:
		event_id: Event ID/name
		registration_data: Optional JSON string with additional data
	
	Returns:
		{
			success: bool,
			registration_id: str,
			status: str,
			message: str,
			waitlist_position: int (if on waitlist)
		}
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login to register for events", frappe.PermissionError)

	# Parse registration data
	if isinstance(registration_data, str):
		try:
			registration_data = json.loads(registration_data)
		except:
			registration_data = {}
	
	if not registration_data:
		registration_data = {}

	# Get event
	try:
		event = frappe.get_doc("Networx Event", event_id)
	except frappe.DoesNotExistError:
		frappe.throw("Event not found")

	# Check if registration is enabled
	if not event.registration_enabled:
		frappe.throw("Registration is not enabled for this event")

	# Check if registration type allows internal registration
	if event.registration_type == "External Link":
		frappe.throw("This event requires external registration. Please use the registration link provided.")

	# Check registration deadline
	now = now_datetime()
	if event.registration_deadline:
		deadline = get_datetime(event.registration_deadline)
		if deadline < now:
			frappe.throw("Registration deadline has passed")

	# Check if already registered
	existing_registration = frappe.db.get_value(
		"Event Registration",
		{
			"event": event_id,
			"user": user,
			"registration_status": ["!=", "Cancelled"]
		},
		["name", "registration_status"],
		as_dict=True
	)

	if existing_registration:
		if existing_registration.registration_status == "Cancelled":
			# Allow re-registration if previously cancelled
			frappe.delete_doc("Event Registration", existing_registration.name, force=1)
		else:
			frappe.throw("You are already registered for this event")

	# Check capacity
	confirmed_count = frappe.db.count(
		"Event Registration",
		{
			"event": event_id,
			"registration_status": ["in", ["Confirmed", "Pending", "Attended"]]
		}
	)

	# Determine registration status
	registration_status = "Pending"
	waitlist_position = 0
	message = "Registration successful"

	if event.max_capacity and event.max_capacity > 0:
		# Event has capacity limit
		available_spots = event.max_capacity - confirmed_count
		
		if available_spots <= 0:
			# Event is full
			if event.waitlist_enabled:
				# Add to waitlist
				waitlist_count = frappe.db.count(
					"Event Registration",
					{
						"event": event_id,
						"registration_status": "Pending",
						"waitlist_position": [">", 0]
					}
				)
				
				# Check waitlist capacity
				if event.waitlist_capacity and event.waitlist_capacity > 0:
					if waitlist_count >= event.waitlist_capacity:
						frappe.throw("Event is full and waitlist is also full")
				
				waitlist_position = waitlist_count + 1
				registration_status = "Pending"
				message = f"You have been added to the waitlist (Position: {waitlist_position})"
			else:
				frappe.throw("Event is full and waitlist is not enabled")
		else:
			# Has capacity
			if event.require_approval:
				registration_status = "Pending"
				message = "Your registration is pending approval"
			elif event.auto_confirm:
				registration_status = "Confirmed"
				message = "Registration confirmed successfully"
			else:
				registration_status = "Pending"
				message = "Registration successful"
	else:
		# Unlimited capacity
		if event.require_approval:
			registration_status = "Pending"
			message = "Your registration is pending approval"
		elif event.auto_confirm:
			registration_status = "Confirmed"
			message = "Registration confirmed successfully"

	# Create registration
	registration = frappe.get_doc({
		"doctype": "Event Registration",
		"event": event_id,
		"user": user,
		"registration_status": registration_status,
		"registration_type": "Internal",
		"waitlist_position": waitlist_position if waitlist_position > 0 else 0
	})

	# Add user_profile link if available
	user_profile = frappe.db.get_value("User Profile", {"user": user}, "name")
	if user_profile:
		registration.user_profile = user_profile

	registration.insert(ignore_permissions=False)

	# Update event analytics
	event.reload()
	event._update_analytics()
	event.save(ignore_permissions=True)

	# Send email notification (if email system is configured)
	try:
		send_registration_email(registration, event, waitlist_position > 0)
	except Exception as e:
		# Don't fail registration if email fails
		frappe.log_error(f"Failed to send registration email: {str(e)}")

	return {
		"success": True,
		"registration_id": registration.name,
		"status": registration_status,
		"message": message,
		"waitlist_position": waitlist_position if waitlist_position > 0 else None
	}


@frappe.whitelist()
def cancel_registration(registration_id, reason=None):
	"""
	Cancel user's registration
	- Move waitlist up if applicable
	- Send cancellation email
	- Update stats
	
	Args:
		registration_id: Registration ID/name
		reason: Optional cancellation reason
	
	Returns:
		{
			success: bool,
			message: str
		}
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login to cancel registration", frappe.PermissionError)

	# Get registration
	try:
		registration = frappe.get_doc("Event Registration", registration_id)
	except frappe.DoesNotExistError:
		frappe.throw("Registration not found")

	# Check permission
	if registration.user != user and "System Manager" not in frappe.get_roles():
		frappe.throw("You don't have permission to cancel this registration", frappe.PermissionError)

	# Check if already cancelled
	if registration.registration_status == "Cancelled":
		frappe.throw("Registration is already cancelled")

	# Get event
	event = frappe.get_doc("Networx Event", registration.event)

	# Update registration
	registration.registration_status = "Cancelled"
	if reason:
		registration.cancellation_reason = reason
	registration.save(ignore_permissions=True)

	# If was confirmed and event has waitlist, promote next person
	if registration.registration_status in ["Confirmed", "Pending"] and registration.waitlist_position == 0:
		if event.waitlist_enabled:
			# Get next person on waitlist
			next_waitlist = frappe.db.get_value(
				"Event Registration",
				{
					"event": registration.event,
					"registration_status": "Pending",
					"waitlist_position": [">", 0]
				},
				["name", "waitlist_position"],
				order_by="waitlist_position ASC",
				as_dict=True
			)

			if next_waitlist:
				# Promote to confirmed
				next_reg = frappe.get_doc("Event Registration", next_waitlist.name)
				next_reg.registration_status = "Confirmed"
				next_reg.waitlist_position = 0
				next_reg.save(ignore_permissions=True)

				# Update other waitlist positions
				frappe.db.sql("""
					UPDATE `tabEvent Registration`
					SET waitlist_position = waitlist_position - 1
					WHERE event = %s
					AND registration_status = 'Pending'
					AND waitlist_position > %s
				""", (registration.event, next_waitlist.waitlist_position))

				# Send promotion email
				try:
					send_waitlist_promotion_email(next_reg, event)
				except Exception as e:
					frappe.log_error(f"Failed to send waitlist promotion email: {str(e)}")

	# Update event analytics
	event.reload()
	event._update_analytics()
	event.save(ignore_permissions=True)

	# Send cancellation email
	try:
		send_cancellation_email(registration, event)
	except Exception as e:
		frappe.log_error(f"Failed to send cancellation email: {str(e)}")

	return {
		"success": True,
		"message": "Registration cancelled successfully"
	}


def send_registration_email(registration, event, is_waitlist=False):
	"""Send registration confirmation email"""
	user_email = frappe.db.get_value("User", registration.user, "email")
	if not user_email:
		return

	subject = f"Registration {'Waitlist' if is_waitlist else 'Confirmed'}: {event.event_name}"
	
	message = f"""
	Dear {frappe.db.get_value('User', registration.user, 'full_name') or 'User'},
	
	{"You have been added to the waitlist" if is_waitlist else "Your registration has been confirmed"} for:
	
	Event: {event.event_name}
	Date: {event.event_date}
	Location: {event.location}
	
	{"Your waitlist position: " + str(registration.waitlist_position) if is_waitlist else ""}
	
	Registration ID: {registration.name}
	
	Thank you!
	"""

	# Use Frappe's email sending (if configured)
	frappe.sendmail(
		recipients=[user_email],
		subject=subject,
		message=message
	)


def send_waitlist_promotion_email(registration, event):
	"""Send email when user is promoted from waitlist"""
	user_email = frappe.db.get_value("User", registration.user, "email")
	if not user_email:
		return

	subject = f"Good News! You're Confirmed: {event.event_name}"
	
	message = f"""
	Dear {frappe.db.get_value('User', registration.user, 'full_name') or 'User'},
	
	Great news! A spot has opened up and your registration for the following event has been confirmed:
	
	Event: {event.event_name}
	Date: {event.event_date}
	Location: {event.location}
	
	Registration ID: {registration.name}
	
	We look forward to seeing you there!
	"""

	frappe.sendmail(
		recipients=[user_email],
		subject=subject,
		message=message
	)


def send_cancellation_email(registration, event):
	"""Send cancellation confirmation email"""
	user_email = frappe.db.get_value("User", registration.user, "email")
	if not user_email:
		return

	subject = f"Registration Cancelled: {event.event_name}"
	
	message = f"""
	Dear {frappe.db.get_value('User', registration.user, 'full_name') or 'User'},
	
	Your registration for the following event has been cancelled:
	
	Event: {event.event_name}
	Date: {event.event_date}
	
	Registration ID: {registration.name}
	
	We hope to see you at future events!
	"""

	frappe.sendmail(
		recipients=[user_email],
		subject=subject,
		message=message
	)

