# Copyright (c) 2025, rajk142567@gmail.com and contributors
# For license information, please see license.txt

import frappe
import random
import re
from frappe import _
from frappe.utils import now_datetime, add_minutes, get_datetime
from frappe.auth import LoginManager


def validate_email(email):
	"""Validate email format"""
	if not email:
		return False
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return bool(re.match(pattern, email))


def get_client_ip():
	"""Get client IP address from request"""
	if frappe.local.request:
		return frappe.local.request.environ.get('REMOTE_ADDR', '')
	return ''


def get_user_agent():
	"""Get user agent from request"""
	if frappe.local.request:
		return frappe.local.request.environ.get('HTTP_USER_AGENT', '')
	return ''


def send_otp_email(email, otp_code):
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
		if not validate_email(email):
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
		expires_at = add_minutes(now_datetime(), 5)
		
		# Get client info
		ip_address = get_client_ip()
		user_agent = get_user_agent()
		
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
		email_sent = send_otp_email(email, otp_code)
		
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
		if not validate_email(email):
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
