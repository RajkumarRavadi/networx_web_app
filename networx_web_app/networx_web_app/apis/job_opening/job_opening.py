import frappe
import json

@frappe.whitelist(allow_guest=True)
def get_job_openings(filters=None, limit=None, offset=None, search_term=None):
    """Get paginated job listings with optional filters"""
    # Handle limit and offset
    try:
        limit = int(limit) if limit is not None else 20
        offset = int(offset) if offset is not None else 0
    except (ValueError, TypeError):
        limit = 20
        offset = 0
    
    # Parse filters if passed as JSON string
    if filters:
        if isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except:
                filters = {}
        elif not isinstance(filters, dict):
            filters = {}
    else:
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
            application_deadline, company_logo, is_external_listing, source_url
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