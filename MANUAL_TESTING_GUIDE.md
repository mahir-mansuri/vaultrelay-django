# Manual Testing Guide for Automatic Account Deletion

## Overview
This guide explains how to manually test the automatic account deletion functionality with the new single email process. Users receive one email after 60 days of inactivity and are automatically deleted after 7 days if they don't respond.

## Test Scenarios

### Scenario 1: Test Inactive User Detection
**Purpose**: Test if inactive users are properly identified and emails are sent.

**Steps**:
1. Create test data:
   ```bash
   python manage.py create_deletion_test_data --scenario inactive
   ```

2. Run the inactivity check:
   ```bash
   python manage.py check_inactive_users
   ```

3. Verify:
   - User should receive inactivity email
   - `inactivity_email_count` should be 1
   - `inactivity_email_sent` should be set to current time
   - `is_marked_for_deletion` should be True (immediately marked for deletion)

### Scenario 2: Test Account Ready for Deletion
**Purpose**: Test accounts that are ready to be deleted after 7 days.

**Steps**:
1. Create ready-to-delete test data:
   ```bash
   python manage.py create_deletion_test_data --scenario ready_to_delete
   ```

2. Run dry run deletion:
   ```bash
   python manage.py auto_delete_inactive_accounts --dry-run
   ```

3. Verify:
   - Should show "DRY RUN MODE - No accounts will be deleted"
   - Should list accounts that would be deleted
   - No actual deletion should occur

### Scenario 3: Test Actual Deletion
**Purpose**: Test the actual deletion process.

**Steps**:
1. Ensure you have ready-to-delete test data:
   ```bash
   python manage.py create_deletion_test_data --scenario ready_to_delete
   ```

2. Run actual deletion:
   ```bash
   python manage.py auto_delete_inactive_accounts
   ```

3. Verify:
   - User should be deleted from database
   - Final email should be sent with user's documents
   - All associated data should be cleaned up

## Manual Database Testing

### Quick Database Updates for Testing

**Make user ready for deletion immediately**:
```python
# In Django shell
from vaultrelay_app.models import UserSignup
from django.utils import timezone
from datetime import timedelta

# Get or create test user
user, created = UserSignup.objects.get_or_create(
    user_email='test_manual@example.com',
    defaults={
        'fname': 'Manual',
        'lname': 'Test',
        'dob': '1990-01-01',
        'trusted_email': 'trusted@example.com',
        'trusted_name': 'Trusted Person',
        'pass1': 'hashed_password',
        'secret': 'test_secret',
    }
)

# Set up for immediate deletion testing
user.last_login = timezone.now() - timedelta(days=70)  # 70 days ago
user.inactivity_email_count = 1  # Received 1 email
user.is_marked_for_deletion = True  # Marked for deletion
user.inactivity_email_sent = timezone.now() - timedelta(days=8)  # Email sent 8 days ago
user.save()

print(f"User {user.user_email} is now ready for deletion testing")
```

**Reset user for fresh testing**:
```python
# Reset user to initial state
user.inactivity_email_count = 0
user.is_marked_for_deletion = False
user.inactivity_email_sent = None
user.save()

print(f"User {user.user_email} has been reset for fresh testing")
```

## Testing Commands Reference

### Check Current Status
```bash
# See all users and their deletion status
python manage.py shell -c "
from vaultrelay_app.models import UserSignup
for user in UserSignup.objects.all():
    print(f'{user.user_email}: Count={user.inactivity_email_count}, Marked={user.is_marked_for_deletion}, LastEmail={user.inactivity_email_sent}')
"
```

### Test Email Sending
```bash
# Test if emails are being sent
python manage.py check_inactive_users
```

### Test Deletion (Dry Run)
```bash
# Safe testing - no actual deletion
python manage.py auto_delete_inactive_accounts --dry-run
```

### Test Deletion (Actual)
```bash
# WARNING: This will actually delete accounts
python manage.py auto_delete_inactive_accounts
```

### Custom Wait Time
```bash
# Test with custom wait time (e.g., 3 days instead of 7)
python manage.py auto_delete_inactive_accounts --days 3
```

## Expected Results

### After Single Email
- User receives email with "Continue Account" and "Delete Account" buttons
- `inactivity_email_count` = 1
- `inactivity_email_sent` = current timestamp
- `is_marked_for_deletion` = True (immediately marked for deletion)

### After 7 Days (Ready for Deletion)
- User is eligible for automatic deletion
- Dry run shows user in deletion list
- Actual deletion removes user and sends final email with documents

## Troubleshooting

### Common Issues
1. **Emails not sending**: Check SMTP settings in settings.py
2. **No users found**: Ensure test data is created properly
3. **Deletion not working**: Check if user is properly marked for deletion

### Debug Commands
```bash
# Check email configuration
python manage.py shell -c "
from django.conf import settings
print('Email backend:', settings.EMAIL_BACKEND)
print('Email host:', settings.EMAIL_HOST)
print('Email user:', settings.EMAIL_HOST_USER)
"

# Check user status
python manage.py shell -c "
from vaultrelay_app.models import UserSignup
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=60)
inactive_users = UserSignup.objects.filter(last_login__lt=cutoff)
print(f'Found {inactive_users.count()} inactive users')

for user in inactive_users:
    print(f'{user.user_email}: Last login {user.last_login}, Emails: {user.inactivity_email_count}')
"
```

## Safety Notes
- Always use `--dry-run` first to see what would be deleted
- Test with non-production data
- Keep backups of important data
- The deletion process sends user's documents via email before deletion

