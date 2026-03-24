# VaultRelay Automatic Account Deletion - Cron Job Configuration

## Overview
This document explains how to set up automatic account deletion for inactive users who don't respond to inactivity emails.

## Process Flow
1. **Check Inactive Users**: Run `check_inactive_users` command to identify users inactive for 2+ months
2. **Send Warning Email**: Send single email with "Continue" or "Delete" options and mark for deletion
3. **Auto Delete**: Run `auto_delete_inactive_accounts` command to delete accounts after 7 days

## Cron Job Setup

### For Linux/Unix Systems
Add these lines to your crontab (`crontab -e`):

```bash
# Check for inactive users and send emails (runs daily at 9 AM)
0 9 * * * cd /path/to/your/django/project && python manage.py check_inactive_users

# Auto-delete accounts marked for deletion (runs daily at 10 AM)
0 10 * * * cd /path/to/your/django/project && python manage.py auto_delete_inactive_accounts
```

### For Windows Systems
Use Windows Task Scheduler to create scheduled tasks:

1. **Task 1 - Check Inactive Users**:
   - Action: Start a program
   - Program: `python`
   - Arguments: `manage.py check_inactive_users`
   - Start in: `C:\path\to\your\django\project`
   - Trigger: Daily at 9:00 AM

2. **Task 2 - Auto Delete Accounts**:
   - Action: Start a program
   - Program: `python`
   - Arguments: `manage.py auto_delete_inactive_accounts`
   - Start in: `C:\path\to\your\django\project`
   - Trigger: Daily at 10:00 AM

## Manual Commands

### Check what would be deleted (dry run)
```bash
python manage.py auto_delete_inactive_accounts --dry-run
```

### Delete accounts with custom wait time
```bash
python manage.py auto_delete_inactive_accounts --days 14
```

### Send inactivity emails
```bash
python manage.py check_inactive_users
```

## Configuration

### Email Settings
Make sure your `settings.py` has proper email configuration:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
SITE_URL = 'http://your-domain.com'  # Update this for production
```

### Timing Configuration
- **Inactivity Period**: 60 days (configurable in `check_inactive_users.py`)
- **Response Time**: 7 days (configurable in `auto_delete_inactive_accounts.py`)
- **Email Frequency**: Single email per user (no second email sent)

## Safety Features

1. **Dry Run Mode**: Test deletions without actually deleting accounts
2. **Email Notifications**: Users receive their files before deletion
3. **Graceful Handling**: Failed deletions are logged and reported
4. **Background Processing**: Deletion happens in background threads
5. **File Recovery**: All user documents are emailed before deletion

## Monitoring

Check the Django logs for:
- Email sending success/failure
- Account deletion progress
- Error messages and exceptions

## Testing

1. **Test Email Sending**:
   ```bash
   python manage.py check_inactive_users
   ```

2. **Test Dry Run Deletion**:
   ```bash
   python manage.py auto_delete_inactive_accounts --dry-run
   ```

3. **Test Actual Deletion** (use with caution):
   ```bash
   python manage.py auto_delete_inactive_accounts
   ```

## Troubleshooting

### Common Issues
1. **Email not sending**: Check SMTP settings and credentials
2. **Permission errors**: Ensure Django has write access to media files
3. **Database errors**: Check database connectivity and permissions

### Logs Location
- Django logs: Check your Django logging configuration
- Cron logs: Usually in `/var/log/cron` (Linux) or Event Viewer (Windows)

