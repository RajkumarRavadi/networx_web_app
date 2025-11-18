# NETWORX Developer Quick Reference

## Common Commands

### Development
```bash
# Start development server
bench start

# Watch for changes (in separate terminal)
bench watch

# Enable developer mode
# Add to site_config.json: "developer_mode": 1

# Clear cache
bench --site your-site clear-cache

# Rebuild assets
bench build --app networx_web_app
```

### Database
```bash
# Run migrations
bench --site your-site migrate

# Access database console
bench --site your-site console

# Backup database
bench --site your-site backup

# Restore database
bench --site your-site restore /path/to/backup
```

### Debugging
```bash
# View logs
bench --site your-site console

# Check error logs
tail -f logs/bench-start.log

# Python debugger in code
import frappe; frappe.db.commit(); frappe.local.response.update({"exc_type": "Debugger"})
```

## File Locations

### DocTypes
```
networx_web_app/networx_web_app/doctype/{doctype_name}/
├── {doctype_name}.json       # DocType definition
├── {doctype_name}.py         # Controller
└── {doctype_name}.js         # Client-side (if needed)
```

### APIs
```
networx_web_app/networx_web_app/api.py
```

### Web Pages
```
networx_web_app/www/
├── page_name.html           # HTML template
└── page_name.py             # Server-side logic
```

### Static Assets
```
networx_web_app/public/
├── css/
│   └── networx.css
└── js/
    ├── api.js
    └── utils.js
```

## Creating New DocTypes

### Via Command Line
```bash
bench --site your-site new-doctype "DocType Name"
```

### Manual Creation
1. Create directory: `networx_web_app/doctype/my_doctype/`
2. Create `my_doctype.json` with DocType definition
3. Create `my_doctype.py` with controller:
```python
import frappe
from frappe.model.document import Document

class MyDoctype(Document):
    def validate(self):
        # Validation logic
        pass
    
    def before_save(self):
        # Logic before saving
        pass
```

## Creating APIs

### Add to api.py
```python
@frappe.whitelist()
def my_api_method(param1, param2=None):
    """API description"""
    # Your logic here
    return {
        "success": True,
        "data": result
    }
```

### Call from Frontend
```javascript
const result = await frappe.call({
    method: 'networx_web_app.networx_web_app.api.my_api_method',
    args: {
        param1: value1,
        param2: value2
    }
});
```

## Creating Web Pages

### 1. Create Python file
```python
# www/my-page.py
import frappe

def get_context(context):
    # Check authentication
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    # Add data to context
    context.page_title = "My Page"
    context.data = get_my_data()
    
    return context
```

### 2. Create HTML file
```html
<!-- www/my-page.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
    <link rel="stylesheet" href="/assets/networx_web_app/css/networx.css">
</head>
<body>
    <!-- Your HTML -->
    
    <script src="/assets/frappe/js/lib/jquery/jquery.min.js"></script>
    <script src="/assets/frappe/js/frappe-web.min.js"></script>
    <script src="/assets/networx_web_app/js/utils.js"></script>
    <script src="/assets/networx_web_app/js/api.js"></script>
    <script>
        // Your JavaScript
    </script>
</body>
</html>
```

## Permission Management

### Check Permissions in Python
```python
if frappe.has_permission("DocType Name", "read"):
    # User has permission
    pass
```

### Set DocType Permissions
1. Open DocType in Desk
2. Scroll to "Permissions" section
3. Add role and set permissions (Read, Write, Create, Delete, etc.)

## Database Queries

### Get single value
```python
value = frappe.db.get_value("DocType", "name", "fieldname")
```

### Get multiple fields
```python
doc = frappe.db.get_value(
    "DocType",
    "name",
    ["field1", "field2"],
    as_dict=True
)
```

### Get list
```python
data = frappe.db.get_all(
    "DocType",
    filters={"status": "Open"},
    fields=["name", "title"],
    limit=10
)
```

### SQL query
```python
result = frappe.db.sql("""
    SELECT * FROM `tabDocType`
    WHERE status = %(status)s
""", {"status": "Open"}, as_dict=True)
```

### Count
```python
count = frappe.db.count("DocType", {"status": "Open"})
```

## Common Frappe Methods

### Document Operations
```python
# Get document
doc = frappe.get_doc("DocType", "name")

# Create new document
doc = frappe.get_doc({
    "doctype": "DocType",
    "field1": "value1"
})
doc.insert()

# Update document
doc.field1 = "new_value"
doc.save()

# Delete document
doc.delete()
```

### User & Session
```python
# Current user
user = frappe.session.user

# User full name
full_name = frappe.session.user_fullname

# Check if logged in
is_logged_in = frappe.session.user != "Guest"

# Get user roles
roles = frappe.get_roles(user)
```

### Utilities
```python
# Today's date
today = frappe.utils.today()

# Current datetime
now = frappe.utils.now()

# Add days
future_date = frappe.utils.add_days(today, 30)

# Format date
formatted = frappe.utils.formatdate(date, "dd-mm-yyyy")

# Throw error
frappe.throw("Error message")

# Show message
frappe.msgprint("Message")
```

## Frontend JavaScript

### Frappe Call
```javascript
frappe.call({
    method: 'path.to.method',
    args: { arg1: 'value' },
    callback: (r) => {
        console.log(r.message);
    }
});
```

### Show Alert
```javascript
frappe.show_alert({
    message: 'Success!',
    indicator: 'green'
}, 5);
```

### Freeze/Unfreeze
```javascript
frappe.freeze();
// Long operation
frappe.unfreeze();
```

### Confirm Dialog
```javascript
frappe.confirm(
    'Are you sure?',
    () => {
        // On yes
    },
    () => {
        // On no
    }
);
```

## Testing

### Create Test Data
```python
# In Python console
doc = frappe.get_doc({
    "doctype": "Job Opening",
    "job_title": "Test Job",
    "company_name": "Test Company",
    "status": "Open"
})
doc.insert(ignore_permissions=True)
```

### Access Python Console
```bash
bench --site your-site console
```

Then:
```python
import frappe
frappe.init(site='your-site')
frappe.connect()

# Your code here
```

## Troubleshooting

### Assets not loading
```bash
bench clear-cache
bench build --app networx_web_app
bench restart
```

### Database errors
```bash
bench --site your-site migrate
bench --site your-site clear-cache
```

### Permission denied
1. Check DocType permissions
2. Verify user has correct role
3. Check permission query conditions

### Page not found
```bash
bench restart
bench clear-website-cache
```

### Python errors
Check logs:
```bash
tail -f logs/bench-start.log
```

## Useful Links

- [Frappe Framework Docs](https://frappeframework.com/docs)
- [Frappe API Docs](https://frappeframework.com/docs/user/en/api)
- [ERPNext Developer Tutorial](https://frappeframework.com/docs/user/en/tutorial)

## Tips & Best Practices

1. **Always use whitelisted methods** for API endpoints
2. **Validate input** in API methods
3. **Use transactions** for related operations
4. **Cache expensive queries** when possible
5. **Log errors** for debugging
6. **Write tests** for critical functionality
7. **Use fixtures** for initial data
8. **Follow naming conventions** (snake_case for Python, camelCase for JS)
9. **Comment complex logic**
10. **Keep functions small** and focused

## Environment Variables

Add to `site_config.json`:
```json
{
    "developer_mode": 1,
    "disable_website_cache": true,
    "server_script_enabled": true
}
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
git add .
git commit -m "Add feature"

# Push to remote
git push origin feature/my-feature

# Create pull request
```

---

Happy Coding! 🚀



