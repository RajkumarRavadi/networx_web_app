app_name = "networx_web_app"
app_title = "Networx Web App"
app_publisher = "rajk142567@gmail.com"
app_description = "A simple full stack web application"
app_email = "rajk142567@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "networx_web_app",
# 		"logo": "/assets/networx_web_app/logo.png",
# 		"title": "Networx Web App",
# 		"route": "/networx_web_app",
# 		"has_permission": "networx_web_app.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/networx_web_app/css/networx_web_app.css"
# app_include_js = "/assets/networx_web_app/js/networx_web_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/networx_web_app/css/networx_web_app.css"
# web_include_js = "/assets/networx_web_app/js/networx_web_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "networx_web_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "networx_web_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# This sets the landing page for the root URL (/) - applies to all users first
home_page = "index"

# website user home page (by Role)
# These redirect logged-in users when they visit root URL to dashboard
# Note: role_home_page takes precedence over home_page for logged-in users
role_home_page = {
	"Student": "dashboard",
    "Website User": "dashboard"
}

# Commented out to allow home_page = "index" to work for guests
# website_user_home_page applies to ALL users (including guests) before home_page is checked
# website_user_home_page = "dashboard"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]
website_route_rules = [
	{"from_route": "/profiles/<slug>", "to_route": "public_profile"},
]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "networx_web_app.utils.jinja_methods",
# 	"filters": "networx_web_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "networx_web_app.install.before_install"
# after_install = "networx_web_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "networx_web_app.uninstall.before_uninstall"
# after_uninstall = "networx_web_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "networx_web_app.utils.before_app_install"
# after_app_install = "networx_web_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "networx_web_app.utils.before_app_uninstall"
# after_app_uninstall = "networx_web_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "networx_web_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"networx_web_app.tasks.all"
# 	],
# 	"daily": [
# 		"networx_web_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"networx_web_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"networx_web_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"networx_web_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "networx_web_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "networx_web_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "networx_web_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["networx_web_app.utils.before_request"]
# after_request = ["networx_web_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["networx_web_app.utils.before_job"]
# after_job = ["networx_web_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"networx_web_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

