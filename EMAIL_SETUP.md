# Email Configuration for NETWORX OTP System

## Overview
The OTP login system requires email configuration to send OTP codes to users. This guide explains how to set up email in Frappe.

## Quick Setup (Development Mode)
If you haven't configured email yet, the system will work in **development mode**:
- OTP will be generated and stored in the database
- OTP will be logged in Frappe error logs
- OTP will be displayed in the browser response (for testing)
- You can manually check the OTP from server logs or database

## Production Email Setup

### Option 1: Gmail SMTP (Easiest for Testing)

1. **Enable App Password in Gmail:**
   - Go to your Google Account settings
   - Security → 2-Step Verification (enable if not already)
   - App Passwords → Generate new app password
   - Copy the 16-character password

2. **Configure in Frappe:**
   - Go to **Desk → Email Account → New**
   - Fill in the details:
     - **Email Account Name:** Gmail Account
     - **Email ID:** your-email@gmail.com
     - **Enable Outgoing:** ✓
     - **SMTP Server:** smtp.gmail.com
     - **Port:** 587
     - **Use TLS:** ✓
     - **Login ID:** your-email@gmail.com
     - **Password:** (paste the 16-character app password)
   - Click **Save**

3. **Set as Default:**
   - After saving, click **Set as Default** button

### Option 2: Other Email Providers

#### Outlook/Hotmail:
- **SMTP Server:** smtp-mail.outlook.com
- **Port:** 587
- **Use TLS:** ✓

#### Yahoo:
- **SMTP Server:** smtp.mail.yahoo.com
- **Port:** 587
- **Use TLS:** ✓

#### Custom SMTP:
- Use your email provider's SMTP settings
- Common ports: 587 (TLS) or 465 (SSL)

### Option 3: Email Domain (For Custom Domains)

1. **Go to:** Desk → Email Domain → New
2. **Configure:**
   - **Domain:** yourdomain.com
   - **Email Server:** mail.yourdomain.com
   - **Port:** 587
   - **Use TLS:** ✓
3. **Create Email Account** linked to this domain

## Testing Email Configuration

1. **Send Test Email:**
   - Go to **Desk → Email Account**
   - Open your email account
   - Click **Send Test Email**
   - Enter your email address
   - Check if you receive the test email

2. **Check Email Queue:**
   - Go to **Desk → Email Queue**
   - Check if emails are being queued
   - Check status (Sent/Failed)

## Troubleshooting

### Emails Not Sending

1. **Check Email Queue:**
   - Desk → Email Queue
   - Look for failed emails
   - Check error messages

2. **Check Server Logs:**
   - Look for email-related errors
   - Check SMTP connection issues

3. **Verify SMTP Settings:**
   - Double-check server, port, and credentials
   - Ensure firewall allows SMTP connections

4. **Gmail Specific:**
   - Make sure "Less secure app access" is enabled (if using password)
   - Or use App Password (recommended)
   - Check if 2FA is enabled

### Development Mode

If email is not configured:
- OTP will still be generated
- OTP will be visible in browser response (dev mode)
- OTP will be logged in Frappe error logs
- Check: Desk → Error Log → Search for "OTP Generated"

## Security Notes

1. **Never commit email credentials to version control**
2. **Use environment variables for production**
3. **Use App Passwords instead of main passwords**
4. **Enable 2FA on email accounts used for SMTP**

## After Configuration

Once email is configured:
1. The OTP system will automatically use email
2. OTPs will be sent to user email addresses
3. Development mode fallback will be disabled
4. Users will receive OTP codes via email

## Quick Test

After setting up email:
1. Go to login page
2. Click "OTP" tab
3. Enter your email
4. Click "Send OTP"
5. Check your email inbox for the OTP code

## Bulk email campaign tool (MVP)

The website page `/bulk_email_campaign` (System Manager only) uses **openpyxl** to read `.xlsx` files with `Name` and `Email` columns. Install app dependencies after pulling changes:

```bash
cd /path/to/frappe-bench
bench setup requirements
# or: bench pip install -e apps/networx_web_app
```

Background sends use `frappe.enqueue` on the **long** queue. Ensure **Redis** is running and a **worker** processes that queue, for example:

```bash
bench worker --queue long,default,short
```

Outgoing mail still uses your **Email Account** as above. Frappe may create **Email Queue** rows for each send; this MVP does not add separate campaign storage.

