from django.core.management.base import BaseCommand
from vaultrelay_app.models import UserSignup
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send email to users inactive for 2 months'

    def handle(self, *args, **kwargs):
        # Calculate cutoff date
        cutoff = timezone.now() - timedelta(days=60)
        print("Cutoff date for inactivity:", cutoff)

        # Query inactive users who haven't been sent an email yet
        inactive_users = UserSignup.objects.filter(
            last_login__lt=cutoff,
            inactivity_email_count=0  # Only users who haven't received any email
        )
        
        print("Found", inactive_users.count(), "inactive users to notify")

        # Send email to each inactive user
        for user in inactive_users:
            subject = 'Your VaultRelay Account is Inactive - Action Required'

            message = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <h2 style="color: #333;">Hi {user.fname},</h2>
                <p style="font-size: 16px;">You haven't logged in for over 2 months. Please choose an action:</p>

                <table cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td>
                      <a href="{settings.SITE_URL}/continue_account/{user.pk}/" style="text-decoration: none;">
                        <span style="display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; border-radius: 6px; font-size: 16px; font-weight: bold;">Continue Account</span>
                      </a>
                    </td>
                    <td style="width: 20px;"></td>
                    <td>
                      <a href="{settings.SITE_URL}/delete_account/{user.pk}/" style="text-decoration: none;">
                        <span style="display: inline-block; background-color: #f44336; color: white; padding: 12px 24px; border-radius: 6px; font-size: 16px; font-weight: bold;">Delete Account</span>
                      </a>
                    </td>
                  </tr>
                </table>

                <p style="margin-top: 20px; font-size: 14px; color: #555;">
                  <strong>Important:</strong> If you do not respond within 7 days, your account will be automatically deleted.
                </p>
                <p style="font-size: 12px; color: #666;">
                  This is your only notification. Please take action to keep your account active.
                </p>
              </body>
            </html>
            """

            try:
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.user_email]
                )
                email.content_subtype = "html"  # Treat message as HTML
                email.send()

                # Update user record to track email sent
                user.inactivity_email_sent = timezone.now()
                user.inactivity_email_count = 1
                user.is_marked_for_deletion = True  # Mark for deletion immediately after first email
                user.save()

                self.stdout.write(self.style.SUCCESS(f"✅ Email sent to {user.user_email} - Account marked for deletion"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to send email to {user.user_email}: {e}"))