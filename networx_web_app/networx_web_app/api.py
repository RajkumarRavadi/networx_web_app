# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
import random
import re
from frappe import _
from frappe.utils import now_datetime, add_to_date, get_datetime
from frappe.auth import LoginManager
from datetime import timedelta


@frappe.whitelist(allow_guest=True)
def get_dashboard_stats():
	"""Get statistics for the student dashboard"""
	user = frappe.session.user
	
	# Get student profile
	student_profile = frappe.db.get_value("Student Profile", {"user": user}, "name")
	
	# Total open jobs
	total_jobs = frappe.db.count("Job Opening", {"status": "Open"})
	
	# Upcoming events (future events)
	upcoming_events = frappe.db.count("Networx Event", {
		"event_date": [">=", frappe.utils.now()]
	})
	
	# Student's application stats
	my_applications = 0
	pending_reviews = 0
	
	if student_profile:
		my_applications = frappe.db.count("Job Application", {
			"student_profile": student_profile
		})
		
		pending_reviews = frappe.db.count("Resume Review", {
			"student_profile": student_profile,
			"status": ["in", ["Pending", "In Review"]]
		})
	
	return {
		"total_jobs": total_jobs,
		"upcoming_events": upcoming_events,
		"my_applications": my_applications,
		"pending_reviews": pending_reviews
	}


@frappe.whitelist(allow_guest=True)
def get_job_listings(filters=None, limit=20, offset=0, search_term=None):
	"""Get paginated job listings with optional filters"""
	try:
		limit = int(limit)
		offset = int(offset)
	except (ValueError, TypeError):
		limit = 20
		offset = 0
	
	# Parse filters if passed as JSON string
	if isinstance(filters, str):
		import json
		try:
			filters = json.loads(filters)
		except:
			filters = {}
	
	if not filters:
		filters = {}
	
	# Always show only open jobs
	filters["status"] = "Open"
	
	# Build the query
	conditions = []
	values = {}
	
	for key, value in filters.items():
		if value:
			conditions.append(f"`{key}` = %({key})s")
			values[key] = value
	
	# Add search functionality
	if search_term:
		conditions.append("(`job_title` LIKE %(search)s OR `company_name` LIKE %(search)s OR `location` LIKE %(search)s)")
		values["search"] = f"%{search_term}%"
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	# Get total count
	total_count = frappe.db.sql(f"""
		SELECT COUNT(*) as count
		FROM `tabJob Opening`
		WHERE {where_clause}
	""", values, as_dict=True)[0].count
	
	# Get jobs
	jobs = frappe.db.sql(f"""
		SELECT 
			name, job_title, company_name, job_type, location, 
			experience_required, salary_range, posted_date, 
			application_deadline, company_logo
		FROM `tabJob Opening`
		WHERE {where_clause}
		ORDER BY posted_date DESC
		LIMIT %(limit)s OFFSET %(offset)s
	""", {**values, "limit": limit, "offset": offset}, as_dict=True)
	
	return {
		"jobs": jobs,
		"total_count": total_count,
		"limit": limit,
		"offset": offset
	}


@frappe.whitelist(allow_guest=True)
def get_job_detail(job_id):
	"""Get detailed information about a specific job"""
	if not job_id:
		frappe.throw(_("Job ID is required"))
	
	job = frappe.get_doc("Job Opening", job_id)
	
	# Check if current user has already applied
	user = frappe.session.user
	student_profile = frappe.db.get_value("Student Profile", {"user": user}, "name")
	
	has_applied = False
	if student_profile:
		has_applied = frappe.db.exists("Job Application", {
			"student_profile": student_profile,
			"job_opening": job_id
		})
	
	return {
		"job": job.as_dict(),
		"has_applied": bool(has_applied)
	}


@frappe.whitelist()
def apply_for_job(job_id, cover_letter=None):
	"""Submit a job application"""
	if not job_id:
		frappe.throw(_("Job ID is required"))
	
	user = frappe.session.user
	
	# Get or create student profile
	student_profile = frappe.db.get_value("Student Profile", {"user": user}, "name")
	
	if not student_profile:
		frappe.throw(_("Please complete your student profile before applying for jobs"))
	
	# Check if job exists and is open
	job = frappe.get_doc("Job Opening", job_id)
	if job.status != "Open":
		frappe.throw(_("This job opening is no longer accepting applications"))
	
	# Create application
	application = frappe.get_doc({
		"doctype": "Job Application",
		"student_profile": student_profile,
		"job_opening": job_id,
		"cover_letter": cover_letter or "",
		"status": "Applied"
	})
	application.insert()
	
	return {
		"success": True,
		"message": "Application submitted successfully",
		"application_id": application.name
	}


@frappe.whitelist(allow_guest=True)
def get_student_profile(user=None):
	"""Get student profile for current or specified user"""
	if not user:
		user = frappe.session.user
	
	profile = frappe.db.get_value(
		"Student Profile",
		{"user": user},
		["name", "user", "full_name", "college", "degree", "graduation_year", 
		 "skills", "bio", "resume_attachment", "linkedin_url", "github_url"],
		as_dict=True
	)
	
	if not profile:
		return {
			"exists": False,
			"user": user
		}
	
	return {
		"exists": True,
		"profile": profile
	}


@frappe.whitelist(allow_guest=True)
def update_student_profile(data):
	"""Create or update student profile"""
	import json
	
	if isinstance(data, str):
		data = json.loads(data)
	
	user = frappe.session.user
	
	# Check if profile exists
	profile_name = frappe.db.get_value("Student Profile", {"user": user}, "name")
	
	if profile_name:
		# Update existing profile
		profile = frappe.get_doc("Student Profile", profile_name)
	else:
		# Create new profile
		profile = frappe.get_doc({
			"doctype": "Student Profile",
			"user": user
		})
	
	# Update fields
	allowed_fields = ["full_name", "college", "degree", "graduation_year", 
					  "skills", "bio", "resume_attachment", "linkedin_url", "github_url"]
	
	for field in allowed_fields:
		if field in data:
			profile.set(field, data[field])
	
	if profile.is_new():
		profile.insert()
	else:
		profile.save()
	
	return {
		"success": True,
		"message": "Profile updated successfully",
		"profile": profile.as_dict()
	}


@frappe.whitelist(allow_guest=True)
def get_student_profile_by_id_or_email(profile_id=None, email=None):
	"""Get complete student profile by profile ID or email
	
	Args:
		profile_id: Student Profile document name (e.g., 'PROF-00001')
		email: User email address
	
	Returns:
		Complete student profile information or error message
	"""
	from frappe import _
	
	if not profile_id and not email:
		frappe.throw(_("Please provide either profile_id or email"))
	
	try:
		# If profile_id is provided, get profile directly
		if profile_id:
			if frappe.db.exists("Student Profile", profile_id):
				profile = frappe.get_doc("Student Profile", profile_id)
			else:
				return {
					"success": False,
					"message": f"Student Profile '{profile_id}' not found"
				}
		# If email is provided, find profile by user field
		elif email:
			profile_name = frappe.db.get_value("Student Profile", {"user": email}, "name")
			if profile_name:
				profile = frappe.get_doc("Student Profile", profile_name)
			else:
				return {
					"success": False,
					"message": f"No Student Profile found for email '{email}'"
				}
		
		# Return complete profile data
		return {
			"success": True,
			"profile": {
				"name": profile.name,
				"user": profile.user,
				"full_name": profile.full_name,
				"college": profile.college,
				"degree": profile.degree,
				"graduation_year": profile.graduation_year,
				"skills": profile.skills,
				"bio": profile.bio,
				"resume_attachment": profile.resume_attachment,
				"linkedin_url": profile.linkedin_url,
				"github_url": profile.github_url,
				"creation": str(profile.creation) if profile.creation else None,
				"modified": str(profile.modified) if profile.modified else None,
				"owner": profile.owner,
				"modified_by": profile.modified_by
			}
		}
	except Exception as e:
		frappe.log_error(f"Error fetching student profile: {str(e)}")
		return {
			"success": False,
			"message": f"Error retrieving profile: {str(e)}"
		}


@frappe.whitelist(allow_guest=True)
def get_recent_events(limit=5):
	"""Get upcoming events"""
	try:
		limit = int(limit)
	except (ValueError, TypeError):
		limit = 5
	
	events = frappe.db.get_all(
		"Networx Event",
		filters={
			"event_date": [">=", frappe.utils.now()]
		},
		fields=["name", "event_name", "event_type", "event_date", "location", "registration_link", "event_banner"],
		order_by="event_date ASC",
		limit=limit
	)
	
	return events




@frappe.whitelist(allow_guest=True)
def get_recent_applications(limit=5):
	"""Get recent job applications for the current user"""
	user = frappe.session.user
	student_profile = frappe.db.get_value("Student Profile", {"user": user}, "name")
	
	if not student_profile:
		return []
		
	applications = frappe.db.get_all(
		"Job Application",
		filters={"student_profile": student_profile},
		fields=["name", "job_opening", "status", "creation", "modified"],
		order_by="creation DESC",
		limit=limit
	)
	
	# Fetch job titles
	for app in applications:
		job = frappe.db.get_value("Job Opening", app.job_opening, ["job_title", "company_name", "company_logo"], as_dict=True)
		if job:
			app.job_title = job.job_title
			app.company_name = job.company_name
			app.company_logo = job.company_logo
			
	return applications


@frappe.whitelist(allow_guest=True)
def get_user_profile_details():
	"""Get detailed profile for the current user"""
	user = frappe.session.user
	if user == "Guest":
		return None
		
	# Get user details (fallback)
	user_details = frappe.db.get_value("User", user, ["user_image", "full_name"], as_dict=True)
	
	# Get User Profile
	profile_name = frappe.db.get_value("User Profile", {"user": user}, "name")
	
	if not profile_name:
		return {
			"full_name": user_details.get("full_name"),
			"user_image": user_details.get("user_image"),
			"email": user
		}
		
	profile = frappe.get_doc("User Profile", profile_name)
	
	# Map fields
	return {
		"name": profile.name,
		"full_name": profile.full_name or user_details.get("full_name"),
		"user_image": profile.profile_image or user_details.get("user_image"),
		"headline": profile.headline or "Student",
		"bio": profile.profile_summary,
		"location": profile.current_location,
		"college": profile.education[0].school if profile.education else "Not set", # Infer from education
		"graduation_year": profile.education[0].end_year if profile.education else "N/A", # Infer from education
		"degree": profile.education[0].degree if profile.education else "N/A", # Infer from education
		"linkedin_url": profile.profile_url,
		"github_url": "", # Extract from contact info if needed
		"skills": profile.skills,
		"experience": profile.experience,
		"education": profile.education,
		"contact_info": profile.contact_info_details
	}

@frappe.whitelist()
def update_user_profile(data):
	"""Update user profile"""
	if isinstance(data, str):
		import json
		data = json.loads(data)
		
	user = frappe.session.user
	profile_name = frappe.db.get_value("User Profile", {"user": user}, "name")
	
	if not profile_name:
		# Create new profile
		profile = frappe.new_doc("User Profile")
		profile.user = user
	else:
		profile = frappe.get_doc("User Profile", profile_name)
		
	# Update fields
	if "full_name" in data: profile.full_name = data["full_name"]
	if "headline" in data: profile.headline = data["headline"]
	if "bio" in data: profile.profile_summary = data["bio"]
	if "location" in data: profile.current_location = data["location"]
	if "linkedin_url" in data: profile.profile_url = data["linkedin_url"]
	
	# Note: Updating child tables (skills, experience, education) requires more complex logic 
	# (clearing and re-adding, or updating specific rows). 
	# For this task, we'll focus on the main fields unless specific child table update logic is requested.
	
	profile.save()
	return profile.name


@frappe.whitelist(allow_guest=True)
def signup(full_name, email, password):
	"""Create a new user and associated profiles"""
	if frappe.db.exists("User", email):
		frappe.throw(_("User with email {0} already exists").format(email))

	# Create User with Administrator privileges
	user = frappe.get_doc({
		"doctype": "User",
		"email": email,
		"first_name": full_name,
		"new_password": password,
		"enabled": 1,
		"send_welcome_email": 0,
		"roles": [{"role": "Student"}]
	})
	user.flags.ignore_permissions = True
	user.insert()

	# Create Student Profile
	student_profile = frappe.get_doc({
		"doctype": "Student Profile",
		"user": email,
		"full_name": full_name
	})
	student_profile.flags.ignore_permissions = True
	student_profile.insert()

	# Create User Profile
	user_profile = frappe.get_doc({
		"doctype": "User Profile",
		"user": email,
		"full_name": full_name,
		"headline": "Student"
	})
	user_profile.flags.ignore_permissions = True
	user_profile.insert()

	# Login the user
	from frappe.auth import LoginManager
	login_manager = LoginManager()
	login_manager.authenticate(user=email, pwd=password)
	login_manager.post_login()

	return {
		"success": True,
		"message": _("User created and logged in successfully")
	}





import frappe

TOTAL_POINTS = 100

@frappe.whitelist()
def get_profile_strength():
	user = frappe.session.user

	profile_name = frappe.db.get_value(
		"User Profile",
		{"user": user},
		"name"
	)

	if not profile_name:
		return _empty_response()

	profile = frappe.get_doc("User Profile", profile_name)

	points = 0
	missing = []

	# ---------- BASIC INFO (40) ----------
	points += 5  # full_name always exists

	if profile.profile_image:
		points += 5
	else:
		missing.append("Add a profile photo")

	if profile.headline:
		points += 5
	else:
		missing.append("Add a headline")

	if profile.industry:
		points += 5
	else:
		missing.append("Add your industry")

	if profile.current_location:
		points += 5
	else:
		missing.append("Add your location")

	if profile.profile_summary and len(profile.profile_summary) >= 50:
		points += 15
	else:
		missing.append("Write a short profile summary (min 50 characters)")

	# ---------- EXPERIENCE & EDUCATION (30) ----------
	if profile.experience:
		points += 15

		if any(e.description and len(e.description) >= 50 for e in profile.experience):
			points += 5
	else:
		missing.append("Add work experience")

	if profile.education:
		points += 10
	else:
		missing.append("Add education details")

	# ---------- SKILLS (10) ----------
	if profile.skills and len(profile.skills) >= 3:
		points += 10
	else:
		missing.append("Add at least 3 skills")

	# ---------- EXTRAS (10) ----------
	if profile.contact_info_details:
		points += 3
	else:
		missing.append("Add contact information")

	if profile.volunteer_experience:
		points += 3

	if profile.awards:
		points += 2

	if profile.is_public:
		points += 2

	percentage = min(100, round((points / TOTAL_POINTS) * 100))

	return {
		"percentage": percentage,
		"earned_points": points,
		"total_points": TOTAL_POINTS,
		"missing": missing
	}


def _empty_response():
	return {
		"percentage": 0,
		"earned_points": 0,
		"total_points": TOTAL_POINTS,
		"missing": [
			"Create your profile to get started"
		]
	}


# ===============================
# OTP AUTHENTICATION APIs
# ===============================

def _validate_email(email):
	"""Validate email format"""
	if not email:
		return False
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return bool(re.match(pattern, email))


def _get_client_ip():
	"""Get client IP address from request"""
	if frappe.local.request:
		return frappe.local.request.environ.get('REMOTE_ADDR', '')
	return ''


def _get_user_agent():
	"""Get user agent from request"""
	if frappe.local.request:
		return frappe.local.request.environ.get('HTTP_USER_AGENT', '')
	return ''


def _send_otp_email(email, otp_code):
	"""Send OTP email to user"""
	subject = "Your NETWORX Login OTP"
	
	html_content = f"""
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="UTF-8">
		<style>
			body {{
				font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
				line-height: 1.6;
				color: #333;
				max-width: 600px;
				margin: 0 auto;
				padding: 20px;
			}}
			.header {{
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				color: white;
				padding: 30px;
				text-align: center;
				border-radius: 10px 10px 0 0;
			}}
			.content {{
				background: #f9fafb;
				padding: 30px;
				border-radius: 0 0 10px 10px;
			}}
			.otp-box {{
				background: white;
				border: 2px solid #667eea;
				border-radius: 8px;
				padding: 20px;
				text-align: center;
				margin: 20px 0;
			}}
			.otp-code {{
				font-size: 32px;
				font-weight: bold;
				color: #667eea;
				letter-spacing: 8px;
				font-family: 'Courier New', monospace;
			}}
			.warning {{
				background: #fff3cd;
				border-left: 4px solid #ffc107;
				padding: 15px;
				margin: 20px 0;
				border-radius: 4px;
			}}
			.footer {{
				margin-top: 30px;
				padding-top: 20px;
				border-top: 1px solid #e5e7eb;
				font-size: 12px;
				color: #6b7280;
				text-align: center;
			}}
		</style>
	</head>
	<body>
		<div class="header">
			<h1 style="margin: 0; font-size: 28px;">NETWORX</h1>
			<p style="margin: 10px 0 0 0; opacity: 0.9;">Login Verification Code</p>
		</div>
		<div class="content">
			<p>Hello,</p>
			<p>You requested a one-time password (OTP) to log in to your NETWORX account.</p>
			
			<div class="otp-box">
				<p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Your OTP Code:</p>
				<div class="otp-code">{otp_code}</div>
			</div>
			
			<div class="warning">
				<strong>⚠️ Security Notice:</strong>
				<ul style="margin: 10px 0 0 0; padding-left: 20px;">
					<li>This OTP is valid for <strong>5 minutes</strong> only</li>
					<li>Do not share this code with anyone</li>
					<li>If you didn't request this code, please ignore this email</li>
				</ul>
			</div>
			
			<p>Enter this code on the login page to complete your authentication.</p>
			
			<div class="footer">
				<p>This is an automated email. Please do not reply.</p>
				<p>&copy; 2025 NETWORX. All rights reserved.</p>
			</div>
		</div>
	</body>
	</html>
	"""
	
	try:
		frappe.sendmail(
			recipients=[email],
			subject=subject,
			message=html_content,
			now=True
		)
		return True
	except Exception as e:
		frappe.log_error(f"Error sending OTP email: {str(e)}")
		return False


@frappe.whitelist(allow_guest=True)
def generate_and_send_otp(email):
	"""Generate and send OTP to user email"""
	try:
		# Validate email format
		if not _validate_email(email):
			return {
				"success": False,
				"message": "Invalid email format"
			}
		
		# Check if user exists
		if not frappe.db.exists("User", email):
			return {
				"success": False,
				"message": "No account found with this email address"
			}
		
		# Check if user is enabled
		user_enabled = frappe.db.get_value("User", email, "enabled")
		if not user_enabled:
			return {
				"success": False,
				"message": "Your account is disabled. Please contact support."
			}
		
		# Invalidate previous unused OTPs for this email
		previous_otps = frappe.get_all(
			"User OTP",
			filters={
				"email": email,
				"is_used": 0
			},
			pluck="name"
		)
		
		if previous_otps:
			for otp_name in previous_otps:
				frappe.delete_doc("User OTP", otp_name, ignore_permissions=True, force=1)
			frappe.db.commit()
		
		# Generate 6-digit OTP
		otp_code = str(random.randint(100000, 999999))
		
		# Set expiry (5 minutes from now)
		expires_at = now_datetime() + timedelta(minutes=5)
		
		# Get client info
		ip_address = _get_client_ip()
		user_agent = _get_user_agent()
		
		# Create OTP record
		otp_doc = frappe.new_doc("User OTP")
		otp_doc.email = email
		otp_doc.otp_code = otp_code
		otp_doc.created_at = now_datetime()
		otp_doc.expires_at = expires_at
		otp_doc.is_used = 0
		otp_doc.ip_address = ip_address
		otp_doc.user_agent = user_agent
		otp_doc.failed_attempts = 0
		otp_doc.flags.ignore_permissions = True
		otp_doc.insert()
		frappe.db.commit()
		
		# Send email
		email_sent = _send_otp_email(email, otp_code)
		
		# Check if email is configured in Frappe (check for any enabled outgoing email account)
		email_accounts = frappe.get_all("Email Account", 
			filters={"enable_outgoing": 1}, 
			limit=1
		)
		email_configured = len(email_accounts) > 0
		
		if not email_sent:
			# In development, if email is not configured, log OTP to console and database
			if not email_configured:
				frappe.logger().info(f"OTP for {email}: {otp_code} (Email not configured - development mode)")
				# Also log to error log so it's visible
				frappe.log_error(
					f"OTP Generated (Email not configured): Email: {email}, OTP: {otp_code}",
					"OTP Generation - Development Mode"
				)
				return {
					"success": True,
					"message": f"OTP generated: {otp_code} (Email not configured - check server logs)",
					"otp_code": otp_code,  # Return OTP in development mode
					"dev_mode": True
				}
			else:
				return {
					"success": False,
					"message": "Failed to send OTP email. Please try again."
				}
		
		return {
			"success": True,
			"message": "OTP has been sent to your email address"
		}
		
	except Exception as e:
		frappe.log_error(f"Error generating OTP: {str(e)}")
		return {
			"success": False,
			"message": "An error occurred. Please try again."
		}


@frappe.whitelist(allow_guest=True)
def verify_otp_and_login(email, otp_code):
	"""Verify OTP and authenticate user"""
	try:
		# Validate inputs
		if not _validate_email(email):
			return {
				"success": False,
				"message": "Invalid email format"
			}
		
		if not otp_code or len(otp_code) != 6 or not otp_code.isdigit():
			return {
				"success": False,
				"message": "Invalid OTP format. Please enter a 6-digit code."
			}
		
		# Find OTP record
		otp_records = frappe.get_all(
			"User OTP",
			filters={
				"email": email,
				"otp_code": otp_code,
				"is_used": 0
			},
			order_by="creation DESC",
			limit=1
		)
		
		if not otp_records:
			# Increment failed attempts for any existing OTP for this email
			existing_otps = frappe.get_all(
				"User OTP",
				filters={
					"email": email,
					"is_used": 0
				},
				pluck="name"
			)
			
			if existing_otps:
				for otp_name in existing_otps:
					otp_doc = frappe.get_doc("User OTP", otp_name)
					otp_doc.failed_attempts = (otp_doc.failed_attempts or 0) + 1
					otp_doc.save(ignore_permissions=True)
				frappe.db.commit()
			
			return {
				"success": False,
				"message": "Invalid OTP code. Please check and try again."
			}
		
		# Get OTP document
		otp_doc = frappe.get_doc("User OTP", otp_records[0].name)
		
		# Check if OTP is valid
		if not otp_doc.is_valid():
			if otp_doc.is_expired():
				return {
					"success": False,
					"message": "OTP has expired. Please request a new one."
				}
			else:
				return {
					"success": False,
					"message": "OTP has already been used. Please request a new one."
				}
		
		# Mark OTP as used
		otp_doc.mark_as_used()
		
		# Verify user exists and is enabled
		if not frappe.db.exists("User", email):
			return {
				"success": False,
				"message": "User account not found"
			}
		
		user = frappe.get_doc("User", email)
		if not user.enabled:
			return {
				"success": False,
				"message": "Your account is disabled. Please contact support."
			}
		
		# Set Frappe session
		# Create login manager and set user
		login_manager = LoginManager()
		login_manager.user = email
		
		# Get user info
		login_manager.get_user_info()
		
		# Create session
		from frappe.sessions import Session
		frappe.local.login_manager = login_manager
		frappe.local.session_obj = Session(
			user=email,
			resume=False,
			full_name=login_manager.info.get("full_name") if login_manager.info else None,
			user_type=login_manager.user_type
		)
		frappe.local.session = frappe.local.session_obj.data
		
		# Run post login setup
		login_manager.setup_boot_cache()
		login_manager.set_user_info()
		
		# Get user profile status
		profile_completed = False
		user_profile = frappe.db.get_value("User Profile", {"user": email}, "name")
		if user_profile:
			profile_completed = True
		
		# Get user data
		user_data = {
			"name": user.name,
			"email": user.email,
			"full_name": user.full_name,
			"user_image": user.user_image,
			"enabled": user.enabled
		}
		
		return {
			"success": True,
			"message": "Login successful",
			"user": user_data,
			"profile_completed": profile_completed
		}
		
	except Exception as e:
		frappe.log_error(f"Error verifying OTP: {str(e)}")
		return {
			"success": False,
			"message": "An error occurred during verification. Please try again."
		}


@frappe.whitelist(allow_guest=True)
def resend_otp(email):
	"""Resend OTP to user email"""
	# Invalidate previous unused OTPs first
	previous_otps = frappe.get_all(
		"User OTP",
		filters={
			"email": email,
			"is_used": 0
		},
		pluck="name"
	)
	
	if previous_otps:
		for otp_name in previous_otps:
			frappe.delete_doc("User OTP", otp_name, ignore_permissions=True, force=1)
		frappe.db.commit()
	
	# Generate and send new OTP
	return generate_and_send_otp(email)


# ===============================
# INSTITUTE SEARCH APIs
# ===============================

@frappe.whitelist(allow_guest=True)
def search_institutes(query, limit=20):
	"""Search institutes by name, slug, or alternate names"""
	try:
		# Parse and validate limit
		try:
			limit = int(limit) if limit else 20
			if limit > 50:
				limit = 50  # Max limit for performance
		except (ValueError, TypeError):
			limit = 20
		
		if not query or len(query.strip()) < 2:
			return {
				"success": True,
				"institutes": [],
				"count": 0
			}
		
		search_term = f"%{query.strip()}%"
		
		# Search across institute_name, institute_slug, and alternate_names
		# Only return active institutes
		institutes = frappe.db.sql("""
			SELECT 
				name,
				institute_name,
				institute_slug,
				institute_type,
				city,
				state,
				country
			FROM `tabInstitute Profile`
			WHERE institute_status = 'Active'
				AND (
					institute_name LIKE %(search)s
					OR institute_slug LIKE %(search)s
					OR alternate_names LIKE %(search)s
				)
			ORDER BY 
				CASE 
					WHEN institute_name LIKE %(exact)s THEN 1
					WHEN institute_name LIKE %(search)s THEN 2
					WHEN institute_slug LIKE %(search)s THEN 3
					ELSE 4
				END,
				institute_name ASC
			LIMIT %(limit)s
		""", {
			"search": search_term,
			"exact": f"{query.strip()}%",
			"limit": limit
		}, as_dict=True)
		
		return {
			"success": True,
			"institutes": institutes,
			"count": len(institutes)
		}
	except Exception as e:
		frappe.log_error(f"Error searching institutes: {str(e)}")
		return {
			"success": False,
			"message": "An error occurred while searching institutes",
			"institutes": [],
			"count": 0
		}


@frappe.whitelist(allow_guest=True)
def get_institute_details(institute_id):
	"""Get full details of a specific institute"""
	try:
		if not institute_id:
			return {
				"success": False,
				"message": "Institute ID is required"
			}
		
		if not frappe.db.exists("Institute Profile", institute_id):
			return {
				"success": False,
				"message": "Institute not found"
			}
		
		institute = frappe.get_doc("Institute Profile", institute_id)
		
		return {
			"success": True,
			"institute": {
				"name": institute.name,
				"institute_name": institute.institute_name,
				"institute_slug": institute.institute_slug,
				"institute_type": institute.institute_type,
				"institute_status": institute.institute_status,
				"city": institute.city,
				"state": institute.state,
				"country": institute.country,
				"website": institute.website,
				"email": institute.email,
				"phone": institute.phone
			}
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting institute details: {str(e)}")
		return {
			"success": False,
			"message": "An error occurred while fetching institute details"
		}
