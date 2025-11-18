# NETWORX Web App - Deployment Checklist

## Pre-Deployment Checklist

### 1. Development Environment ✅
- [x] App created and tested locally
- [x] All DocTypes created and working
- [x] APIs tested and functioning
- [x] Web pages loading correctly
- [x] Authentication working
- [x] Sample data loads on installation

### 2. Code Quality
- [ ] Code reviewed
- [ ] No console errors in browser
- [ ] No Python errors in logs
- [ ] All functions documented
- [ ] Clean git history

### 3. Configuration Files
- [ ] `hooks.py` properly configured
- [ ] `setup.py` tested
- [ ] Permissions set correctly on DocTypes
- [ ] Fixtures working

## Installation Steps

### On Fresh Site

```bash
# 1. Navigate to bench directory
cd /home/frappeuser/frappe-bench

# 2. Install the app on site
bench --site your-site-name install-app networx_web_app

# 3. Run migrations
bench --site your-site-name migrate

# 4. Build assets
bench build --app networx_web_app

# 5. Clear cache
bench --site your-site-name clear-cache

# 6. Restart bench
bench restart
```

### Verify Installation

1. Check if Student role was created:
   ```bash
   bench --site your-site-name console
   ```
   ```python
   frappe.db.exists("Role", "Student")
   # Should return "Student"
   ```

2. Check if test student was created:
   - Login to Desk
   - Go to User List
   - Look for `student@networx.test`

3. Check if sample data was created:
   - Job Opening: Should have 3 entries
   - Networx Event: Should have 3 entries

4. Test the web interface:
   - Visit: `http://your-site:8000/login`
   - Login with: `student@networx.test` / `student123`
   - Check dashboard loads
   - Check jobs page loads
   - Try applying for a job

## Production Deployment

### 1. Server Requirements
- [ ] Ubuntu/Debian server
- [ ] Python 3.10+
- [ ] Node.js 18+
- [ ] MariaDB/PostgreSQL
- [ ] Nginx
- [ ] SSL certificate

### 2. Frappe Bench Setup
```bash
# Install Frappe
bench init frappe-bench --frappe-branch version-15

# Create site
cd frappe-bench
bench new-site your-domain.com

# Install app
bench get-app https://github.com/yourusername/networx_web_app
bench --site your-domain.com install-app networx_web_app

# Setup production
sudo bench setup production your-user
```

### 3. Configuration

#### site_config.json
```json
{
  "db_name": "_your_db_name",
  "db_password": "your_password",
  "developer_mode": 0,
  "disable_website_cache": false,
  "dns_multitenant": true,
  "host_name": "https://your-domain.com",
  "mail_server": "smtp.gmail.com",
  "mail_port": 587,
  "use_ssl": 1,
  "mail_login": "your-email@gmail.com",
  "mail_password": "your-app-password",
  "auto_email_id": "noreply@your-domain.com",
  "always_use_account_email_id_as_sender": 1
}
```

### 4. SSL Setup
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 5. Nginx Configuration
```nginx
# Should be auto-configured by bench setup production
# Located at: /etc/nginx/conf.d/frappe-bench.conf

# Verify it includes:
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of config
}
```

### 6. Database Backups
```bash
# Setup automated backups
bench --site your-domain.com backup --with-files

# Add to crontab (daily at 2 AM)
0 2 * * * cd /home/frappe/frappe-bench && /home/frappe/.local/bin/bench --site your-domain.com backup --with-files >> /home/frappe/backup.log 2>&1
```

### 7. Security Checklist
- [ ] Disable developer mode
- [ ] Change Administrator password
- [ ] Remove test users
- [ ] Configure CORS if needed
- [ ] Enable rate limiting
- [ ] Set up fail2ban
- [ ] Configure firewall (UFW)
- [ ] Regular security updates

### 8. Performance Optimization
```bash
# Enable Redis cache
bench --site your-domain.com enable-scheduler

# Background workers
bench setup supervisor
bench setup redis

# Restart services
sudo supervisorctl restart all
```

### 9. Monitoring Setup

#### Install monitoring tools
```bash
# Frappe Monitor
bench install-app frappe_monitor

# Or external tools
# - New Relic
# - DataDog
# - Uptime Robot
```

#### Log monitoring
```bash
# Check error logs
tail -f logs/bench-start.log
tail -f logs/error.log

# Nginx logs
tail -f /var/log/nginx/error.log
```

### 10. Email Configuration

Test email sending:
```python
frappe.sendmail(
    recipients=['test@example.com'],
    subject='Test Email',
    message='This is a test email from NETWORX'
)
```

### 11. Custom Domain Setup

1. Update DNS records:
   - A record: your-domain.com → server-ip
   - CNAME: www.your-domain.com → your-domain.com

2. Update bench:
   ```bash
   bench setup add-domain your-domain.com --site site-name
   ```

3. Regenerate nginx config:
   ```bash
   bench setup nginx
   sudo service nginx reload
   ```

## Post-Deployment

### 1. User Management
- [ ] Remove test student user (or change password)
- [ ] Create real admin users
- [ ] Set up proper roles and permissions
- [ ] Configure email notifications

### 2. Content Setup
- [ ] Remove sample jobs
- [ ] Add real job openings
- [ ] Remove sample events
- [ ] Add real events
- [ ] Update branding (logo, colors)

### 3. Testing Checklist
- [ ] Login/Logout works
- [ ] Dashboard loads correctly
- [ ] Jobs can be viewed and filtered
- [ ] Job applications work
- [ ] Email notifications work
- [ ] Mobile responsive
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

### 4. SEO & Analytics
- [ ] Add Google Analytics
- [ ] Configure meta tags
- [ ] Add sitemap
- [ ] Set up robots.txt
- [ ] Add social media tags

### 5. Legal & Compliance
- [ ] Add Privacy Policy page
- [ ] Add Terms of Service page
- [ ] Add Cookie Policy
- [ ] GDPR compliance (if applicable)
- [ ] Add Contact information

## Maintenance Schedule

### Daily
- Check error logs
- Monitor disk space
- Check application performance

### Weekly
- Review application logs
- Check database size
- Review user feedback

### Monthly
- Update Frappe/ERPNext
- Security audit
- Performance review
- Backup verification

### Quarterly
- SSL certificate renewal check
- Review and update documentation
- Security patches
- Feature updates

## Troubleshooting

### Common Issues

1. **Assets not loading**
   ```bash
   bench clear-cache
   bench build --app networx_web_app
   sudo supervisorctl restart all
   ```

2. **Database connection issues**
   ```bash
   bench --site your-site mariadb
   # Check if you can connect
   ```

3. **Nginx errors**
   ```bash
   sudo nginx -t
   sudo service nginx restart
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot renew
   sudo service nginx reload
   ```

5. **Worker not running**
   ```bash
   bench doctor
   sudo supervisorctl restart all
   ```

## Rollback Plan

If deployment fails:

1. **Restore database backup**
   ```bash
   bench --site your-site restore /path/to/backup.sql.gz
   ```

2. **Revert code changes**
   ```bash
   cd apps/networx_web_app
   git checkout previous-stable-tag
   bench --site your-site migrate
   ```

3. **Clear cache and rebuild**
   ```bash
   bench clear-cache
   bench build
   sudo supervisorctl restart all
   ```

## Support Contacts

- **Technical Support**: support@thenetworx.live
- **Emergency Contact**: +91 9381964965
- **Documentation**: See README.md, SETUP_INSTRUCTIONS.md

## Success Metrics

Track these after deployment:
- [ ] Page load times < 2 seconds
- [ ] API response times < 500ms
- [ ] Zero critical errors in logs
- [ ] User registration rate
- [ ] Job application rate
- [ ] User satisfaction scores

---

## Final Verification

Before going live, ensure:
- ✅ All tests pass
- ✅ No errors in logs
- ✅ SSL certificate valid
- ✅ Backups configured
- ✅ Monitoring active
- ✅ Email working
- ✅ DNS configured
- ✅ Documentation updated

## Go Live! 🚀

```bash
# Final restart
sudo supervisorctl restart all

# Clear all caches
bench --site your-site clear-cache
bench --site your-site clear-website-cache

# Check status
bench doctor
```

**Your NETWORX Web App is now live!** 🎉

Monitor closely for the first 24-48 hours and be ready to address any issues quickly.

---

**Need Help?** Contact support@thenetworx.live



