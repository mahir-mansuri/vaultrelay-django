from django.core.management.base import BaseCommand
from vaultrelay_app.models import UserSignup
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Create test data for manual testing of automatic account deletion'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            type=str,
            choices=['inactive', 'marked_for_deletion', 'ready_to_delete'],
            default='inactive',
            help='Test scenario to create'
        )

    def handle(self, *args, **options):
        scenario = options['scenario']
        
        if scenario == 'inactive':
            self.create_inactive_user()
        elif scenario == 'marked_for_deletion':
            self.create_marked_for_deletion_user()
        elif scenario == 'ready_to_delete':
            self.create_ready_to_delete_user()

    def create_inactive_user(self):
        """Create a user who is inactive for 60+ days but hasn't received emails yet"""
        old_date = timezone.now() - timedelta(days=65)
        
        test_user, created = UserSignup.objects.get_or_create(
            user_email='test_inactive@example.com',
            defaults={
                'fname': 'Test',
                'lname': 'Inactive',
                'dob': '1990-01-01',
                'trusted_email': 'trusted@example.com',
                'trusted_name': 'Trusted Person',
                'pass1': make_password('123456'),
                'secret': 'test_secret',
                'last_login': old_date,
                'inactivity_email_count': 0,
                'is_marked_for_deletion': False,
                'inactivity_email_sent': None,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created inactive test user: {test_user.user_email}"))
            self.stdout.write(f"   Last login: {test_user.last_login}")
            self.stdout.write(f"   Email count: {test_user.inactivity_email_count}")
            self.stdout.write(f"   Marked for deletion: {test_user.is_marked_for_deletion}")
        else:
            # Update existing user
            test_user.last_login = old_date
            test_user.inactivity_email_count = 0
            test_user.is_marked_for_deletion = False
            test_user.inactivity_email_sent = None
            test_user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Updated inactive test user: {test_user.user_email}"))

    def create_marked_for_deletion_user(self):
        """Create a user who has received 1 email and is marked for deletion"""
        old_date = timezone.now() - timedelta(days=70)
        email_sent_date = timezone.now() - timedelta(days=3)  # 3 days ago
        
        test_user, created = UserSignup.objects.get_or_create(
            user_email='test_marked@example.com',
            defaults={
                'fname': 'Test',
                'lname': 'Marked',
                'dob': '1990-01-01',
                'trusted_email': 'trusted2@example.com',
                'trusted_name': 'Trusted Person 2',
                'pass1': make_password('123456'),
                'secret': 'test_secret2',
                'last_login': old_date,
                'inactivity_email_count': 1,
                'is_marked_for_deletion': True,
                'inactivity_email_sent': email_sent_date,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created marked test user: {test_user.user_email}"))
            self.stdout.write(f"   Last login: {test_user.last_login}")
            self.stdout.write(f"   Email count: {test_user.inactivity_email_count}")
            self.stdout.write(f"   Marked for deletion: {test_user.is_marked_for_deletion}")
            self.stdout.write(f"   Email sent: {test_user.inactivity_email_sent}")
        else:
            # Update existing user
            test_user.last_login = old_date
            test_user.inactivity_email_count = 1
            test_user.is_marked_for_deletion = True
            test_user.inactivity_email_sent = email_sent_date
            test_user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Updated marked test user: {test_user.user_email}"))

    def create_ready_to_delete_user(self):
        """Create a user who is ready to be deleted (email sent 8+ days ago)"""
        old_date = timezone.now() - timedelta(days=75)
        email_sent_date = timezone.now() - timedelta(days=8)  # 8 days ago
        
        test_user, created = UserSignup.objects.get_or_create(
            user_email='test_ready@example.com',
            defaults={
                'fname': 'Test',
                'lname': 'Ready',
                'dob': '1990-01-01',
                'trusted_email': 'trusted3@example.com',
                'trusted_name': 'Trusted Person 3',
                'pass1': make_password('123456'),
                'secret': 'test_secret3',
                'last_login': old_date,
                'inactivity_email_count': 1,
                'is_marked_for_deletion': True,
                'inactivity_email_sent': email_sent_date,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created ready-to-delete test user: {test_user.user_email}"))
            self.stdout.write(f"   Last login: {test_user.last_login}")
            self.stdout.write(f"   Email count: {test_user.inactivity_email_count}")
            self.stdout.write(f"   Marked for deletion: {test_user.is_marked_for_deletion}")
            self.stdout.write(f"   Email sent: {test_user.inactivity_email_sent}")
        else:
            # Update existing user
            test_user.last_login = old_date
            test_user.inactivity_email_count = 1
            test_user.is_marked_for_deletion = True
            test_user.inactivity_email_sent = email_sent_date
            test_user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Updated ready-to-delete test user: {test_user.user_email}"))

