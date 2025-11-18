# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_install():
	"""Setup NETWORX app after installation"""
	try:
		# Create Student role if not exists
		create_student_role()
		
		# Create sample student user
		create_sample_student()
		
		# Create sample job openings
		create_sample_jobs()
		
		# Create sample events
		create_sample_events()
		
		frappe.db.commit()
		
		print("\n" + "="*60)
		print("NETWORX App Setup Complete!")
		print("="*60)
		print("\nTest Student Login:")
		print("  Username: student@networx.test")
		print("  Password: student123")
		print("\nAccess the app at: http://your-site:8000/login")
		print("="*60 + "\n")
		
	except Exception as e:
		frappe.log_error(f"Error in after_install: {str(e)}")
		print(f"Setup error: {str(e)}")


def create_student_role():
	"""Create Student role"""
	if not frappe.db.exists("Role", "Student"):
		role = frappe.get_doc({
			"doctype": "Role",
			"role_name": "Student",
			"desk_access": 0,
			"disabled": 0
		})
		role.insert(ignore_permissions=True)
		print("✓ Created Student role")
	else:
		print("✓ Student role already exists")


def create_sample_student():
	"""Create a sample student user"""
	email = "student@networx.test"
	
	if not frappe.db.exists("User", email):
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": "Test",
			"last_name": "Student",
			"enabled": 1,
			"send_welcome_email": 0,
			"new_password": "student123"
		})
		user.insert(ignore_permissions=True)
		
		# Add Student role
		user.add_roles("Student")
		
		# Create student profile
		profile = frappe.get_doc({
			"doctype": "Student Profile",
			"user": email,
			"full_name": "Test Student",
			"college": "University of Technology",
			"degree": "B.Tech Computer Science",
			"graduation_year": 2025,
			"skills": "Python, JavaScript, React, SQL",
			"bio": "<p>Passionate computer science student looking for opportunities in web development.</p>"
		})
		profile.insert(ignore_permissions=True)
		
		print(f"✓ Created test student: {email} (password: student123)")
	else:
		print("✓ Test student already exists")


def create_sample_jobs():
	"""Create sample job openings"""
	jobs = [
		{
			"job_title": "Frontend Developer Intern",
			"company_name": "TechCorp Solutions",
			"job_type": "Internship",
			"location": "Remote",
			"experience_required": "0-1 years",
			"salary_range": "$500-$800/month",
			"status": "Open",
			"description": "<p>We are looking for a passionate frontend developer intern to join our team. You will work on real-world projects using React, TypeScript, and modern web technologies.</p>",
			"requirements": "<ul><li>Basic knowledge of HTML, CSS, JavaScript</li><li>Familiarity with React or similar frameworks</li><li>Good problem-solving skills</li><li>Ability to work in a team</li></ul>",
			"posted_date": frappe.utils.today(),
			"application_deadline": frappe.utils.add_days(frappe.utils.today(), 30)
		},
		{
			"job_title": "Full Stack Developer",
			"company_name": "InnovateLabs",
			"job_type": "Full-time",
			"location": "Bangalore, India",
			"experience_required": "1-2 years",
			"salary_range": "$40,000-$60,000/year",
			"status": "Open",
			"description": "<p>Join our dynamic team as a Full Stack Developer. Work on cutting-edge projects using modern tech stack including Node.js, React, and cloud technologies.</p>",
			"requirements": "<ul><li>1+ years of experience in web development</li><li>Proficiency in JavaScript/TypeScript</li><li>Experience with React and Node.js</li><li>Knowledge of databases (SQL/NoSQL)</li><li>Experience with Git and Agile methodologies</li></ul>",
			"posted_date": frappe.utils.today(),
			"application_deadline": frappe.utils.add_days(frappe.utils.today(), 45)
		},
		{
			"job_title": "Data Science Intern",
			"company_name": "DataViz Analytics",
			"job_type": "Internship",
			"location": "Hyderabad, India",
			"experience_required": "Fresher",
			"salary_range": "$400-$700/month",
			"status": "Open",
			"description": "<p>Exciting opportunity for data science enthusiasts to work on real-world data analytics projects. Learn from experienced data scientists and contribute to meaningful projects.</p>",
			"requirements": "<ul><li>Strong foundation in Python</li><li>Basic knowledge of ML/AI concepts</li><li>Familiarity with pandas, numpy, matplotlib</li><li>Good analytical and problem-solving skills</li></ul>",
			"posted_date": frappe.utils.today(),
			"application_deadline": frappe.utils.add_days(frappe.utils.today(), 20)
		}
	]
	
	created = 0
	for job_data in jobs:
		# Check if similar job exists
		if not frappe.db.exists("Job Opening", {"job_title": job_data["job_title"], "company_name": job_data["company_name"]}):
			job = frappe.get_doc({
				"doctype": "Job Opening",
				**job_data
			})
			job.insert(ignore_permissions=True)
			created += 1
	
	if created > 0:
		print(f"✓ Created {created} sample job openings")
	else:
		print("✓ Sample jobs already exist")


def create_sample_events():
	"""Create sample events"""
	events = [
		{
			"event_name": "Web Development Bootcamp 2025",
			"event_type": "Workshop",
			"event_date": frappe.utils.add_days(frappe.utils.now(), 10),
			"location": "Online",
			"description": "<p>Join our intensive 3-day web development bootcamp covering HTML, CSS, JavaScript, and React. Perfect for beginners and intermediate learners.</p>",
			"registration_link": "https://thenetworx.live/events/bootcamp"
		},
		{
			"event_name": "Annual Hackathon 2025",
			"event_type": "Hackathon",
			"event_date": frappe.utils.add_days(frappe.utils.now(), 30),
			"location": "Bangalore, India",
			"description": "<p>48-hour hackathon with exciting prizes! Build innovative solutions to real-world problems. Win prizes worth $10,000.</p>",
			"registration_link": "https://thenetworx.live/events/hackathon"
		},
		{
			"event_name": "Career Fair - Tech Companies",
			"event_type": "Career Fair",
			"event_date": frappe.utils.add_days(frappe.utils.now(), 15),
			"location": "Hyderabad, India",
			"description": "<p>Meet recruiters from top tech companies. On-spot interviews and networking opportunities with industry leaders.</p>",
			"registration_link": "https://thenetworx.live/events/career-fair"
		}
	]
	
	created = 0
	for event_data in events:
		# Check if similar event exists
		if not frappe.db.exists("Networx Event", {"event_name": event_data["event_name"]}):
			event = frappe.get_doc({
				"doctype": "Networx Event",
				**event_data
			})
			event.insert(ignore_permissions=True)
			created += 1
	
	if created > 0:
		print(f"✓ Created {created} sample events")
	else:
		print("✓ Sample events already exist")



