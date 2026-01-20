import json

import frappe
from frappe.utils import cint


@frappe.whitelist()
def update_user_profile(data=None, user=None):
    """Create or update a User Profile including all fields and child tables.

    Expected payload (as dict or JSON string):
    {
        "user": "user@example.com",            # optional, defaults to session user
        "full_name": "Preferred Name",
        "profile_image": "/files/...",
        "headline": "...",
        "current_location": "...",
        "profile_url": "...",
        "industry": "...",
        "profile_summary": "<div>...</div>",
        "contact_info_details": [ { ... }, ... ],
        "experience": [ { ... }, ... ],
        "education": [ { ... }, ... ],
        "skills": [ { ... }, ... ],
        "certifications": [ { ... }, ... ],
        "volunteer_experience": [ { ... }, ... ],
        "awards": [ { ... }, ... ],
        "projects": [ { ... }, ... ]
    }
    """

    # Parse incoming data
    if isinstance(data, str):
        data = data.strip()
        data = json.loads(data) if data else {}

    if data is None:
        data = {}

    if not isinstance(data, dict):
        frappe.throw("Invalid data format for user profile update. Expected JSON object.")

    # Resolve user
    if not user:
        user = data.get("user") or frappe.session.user

    if not user or user == "Guest":
        frappe.throw("Please login to update your profile.")

    data["user"] = user

    # Get or create User Profile for this user
    profile_name = frappe.db.get_value("User Profile", {"user": user}, "name")

    if profile_name:
        profile = frappe.get_doc("User Profile", profile_name)
    else:
        profile = frappe.new_doc("User Profile")
        profile.user = user

    # Update simple fields
    main_fields = [
        "full_name",
        "profile_image",
        "headline",
        "current_location",
        "profile_url",
        "industry",
        "profile_summary",
        "public_slug",
    ]

    for field in main_fields:
        if field in data:
            profile.set(field, data[field])

    if "is_public" in data:
        profile.is_public = cint(data.get("is_public"))

    # Helper to clean child row dictionaries
    def clean_child_row(row):
        if not isinstance(row, dict):
            return {}

        skip_keys = {
            "name",
            "doctype",
            "owner",
            "creation",
            "modified",
            "modified_by",
            "parent",
            "parentfield",
            "parenttype",
            "idx",
            "docstatus",
        }
        return {k: v for k, v in row.items() if k not in skip_keys}

    # Child table fields on User Profile
    child_tables = [
        "contact_info_details",
        "experience",
        "education",
        "skills",
        "certifications",
        "volunteer_experience",
        "awards",
        "projects",
    ]

    for table_field in child_tables:
        if table_field in data:
            # Replace existing child table rows with provided data
            profile.set(table_field, [])
            rows = data.get(table_field) or []

            for row in rows:
                cleaned = clean_child_row(row)
                if cleaned:
                    # Special handling for projects: validate institute link
                    if table_field == "projects" and cleaned.get("institute"):
                        institute_value = cleaned.get("institute")
                        # Check if it's a valid link to Institute Profile
                        if not frappe.db.exists("Institute Profile", institute_value):
                            # Invalid link - move to institute_name and clear institute
                            if not cleaned.get("institute_name"):
                                cleaned["institute_name"] = institute_value
                            cleaned["institute"] = None
                    
                    profile.append(table_field, cleaned)

    # Save document
    if profile.is_new():
        profile.insert()
    else:
        profile.save()

    frappe.db.commit()

    return {
        "success": True,
        "message": "User profile updated successfully",
        "profile": profile.as_dict(),
    }
