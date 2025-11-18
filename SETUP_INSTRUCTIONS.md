# NETWORX Web App - Setup Instructions

## Overview

A complete student networking and job portal platform built on Frappe Framework. This app provides students with a dedicated portal to browse jobs, apply for positions, track applications, and stay updated with events and hackathons.

## Features

✅ **Custom Login Page** - Beautiful, modern login interface for students
✅ **Dashboard** - Analytics and quick access to jobs, events, and applications
✅ **Job Listings** - Browse, search, and filter job openings
✅ **Job Details** - View detailed job information and apply directly
✅ **Student Profiles** - Manage personal information, skills, and resume
✅ **Events & Hackathons** - Stay updated with upcoming events
✅ **Resume Reviews** - Track resume review requests and feedback

## Installation Steps

### 1. Install the App (if not already done)

```bash
cd /home/frappeuser/frappe-bench
bench get-app https://github.com/yourusername/networx_web_app
# OR if developing locally
bench get-app /path/to/networx_web_app
```

### 2. Install App on Site

```bash
bench --site your-site-name install-app networx_web_app
```

### 3. Migrate Database

```bash
bench --site your-site-name migrate
```

### 4. Build Assets

```bash
bench build --app networx_web_app
```

### 5. Restart Bench

```bash
bench restart
```

## Post-Installation Setup

### 1. Create the Student Role (if not auto-created)

Go to: `Desk > Role > New Role`
- Role Name: **Student**
- Desk Access: **No** (unchecked)

### 2. Create a Test Student User

Go to: `Desk > User > New User`
- Email: student@example.com
- First Name: Test
- Last Name: Student
- Roles: Add "Student" role
- Send Welcome Email: No

### 3. Create Sample Data (Optional)

#### Create Job Openings

Go to: `Desk > Job Opening > New Job Opening`

Example:
- Job Title: Frontend Developer Intern
- Company Name: TechCorp
- Job Type: Internship
- Location: Remote
- Status: Open
- Description: Add job description
- Requirements: Add requirements

#### Create Events

Go to: `Desk > Networx Event > New Networx Event`

Example:
- Event Name: Web Development Hackathon 2025
- Event Type: Hackathon
- Event Date: Future date
- Location: Online
- Description: Add event description

### 4. Test the Application

1. **Open the login page:**
   - Navigate to: `http://your-site:8000/login`
   - Login with student credentials

2. **Access Dashboard:**
   - After login, you should be redirected to `/dashboard`
   - View stats and featured jobs

3. **Browse Jobs:**
   - Navigate to `/jobs`
   - Filter and search jobs
   - Click on a job to view details

4. **Apply for Jobs:**
   - Open a job detail page
   - Click "Apply Now"
   - Submit application with cover letter

## DocTypes Created

### Student Profile
Stores student information including:
- Personal details
- Education info
- Skills
- Resume and portfolio links

### Job Opening
Job postings with:
- Company info
- Job details
- Requirements
- Application deadline

### Job Application
Tracks student applications:
- Student profile link
- Job opening link
- Application status
- Cover letter

### Networx Event
Events and activities:
- Event details
- Date and location
- Registration links

### Resume Review
Resume feedback system:
- Review status
- Reviewer assignment
- Feedback notes

## API Endpoints

All APIs are located in `networx_web_app/networx_web_app/api.py`

- `get_dashboard_stats()` - Dashboard statistics
- `get_job_listings()` - Paginated job listings with filters
- `get_job_detail()` - Detailed job information
- `apply_for_job()` - Submit job application
- `get_student_profile()` - Get student profile data
- `update_student_profile()` - Update student profile
- `get_recent_events()` - Upcoming events

## Web Pages

- `/login` - Custom login page
- `/dashboard` - Student dashboard
- `/jobs` - Job listings page
- `/job-detail?id=JOB-XXXXX` - Job detail page

## Customization

### Styling

Edit `/networx_web_app/public/css/networx.css` to customize:
- Colors and theme
- Typography
- Card styles
- Button styles

### Branding

Update the following in web pages:
- Navbar brand text
- Login page logo
- Color scheme variables in CSS

### Adding New Features

1. Create new DocTypes in `/networx_web_app/doctype/`
2. Add API methods in `api.py`
3. Create new web pages in `/www/`
4. Update hooks.py if needed

## Troubleshooting

### Assets not loading

```bash
bench clear-cache
bench build --app networx_web_app
bench restart
```

### Database errors

```bash
bench --site your-site-name migrate
bench --site your-site-name clear-cache
```

### Permission errors

Check that:
- Student role has proper permissions on DocTypes
- User has Student role assigned
- DocType permissions are configured correctly

### Page not found

```bash
bench restart
bench clear-website-cache
```

## Development

### Enable Developer Mode

In `site_config.json`:
```json
{
  "developer_mode": 1
}
```

### Watch for changes

```bash
bench watch
```

### Check logs

```bash
bench --site your-site-name console
```

## Production Deployment

1. Disable developer mode
2. Set up proper database backups
3. Configure SSL certificates
4. Set up proper email settings
5. Enable security features in Frappe

## Support

For issues and questions:
- Check Frappe documentation: https://frappeframework.com/docs
- Review code in the repository
- Contact: support@thenetworx.live

## License

MIT License

## Credits

Built for NETWORX - Connecting Talent with Opportunity



