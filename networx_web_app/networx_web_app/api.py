# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


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
		job = frappe.db.get_value("Job Opening", app.job_opening, ["job_title", "company_name"], as_dict=True)
		if job:
			app.job_title = job.job_title
			app.company_name = job.company_name
			
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

