from vaultrelay_app.models import UserSignup

print("Checking if user exists...")
try:
    user = UserSignup.objects.get(user_email='test_ready@example.com')
    print('User still exists:', user.user_email)
except UserSignup.DoesNotExist:
    print('✅ User successfully deleted!')

print("\nAll remaining users:")
for user in UserSignup.objects.all():
    print(f"- {user.user_email}: Emails={user.inactivity_email_count}, Marked={user.is_marked_for_deletion}")

