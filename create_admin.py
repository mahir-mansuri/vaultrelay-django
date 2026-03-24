"""
Script to create Django superuser for VaultRelay admin panel
Run this script to automatically create an admin account
Usage: python create_admin.py [username] [password] [email]
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaultrelay.settings')
django.setup()

from django.contrib.auth.models import User

# Get username and password from command line arguments or use defaults
if len(sys.argv) >= 3:
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) >= 4 else f'{username}@vaultrelay.com'
else:
    # Default values if not provided
    username = 'vaultrelay'
    email = 'vaultrelay@vaultrelay.com'
    password = 'vaultrelay12'
    print("Usage: python create_admin.py [username] [password] [email]")
    print("Using default credentials. Provide arguments to customize.")

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✓ Updated existing user '{username}' with admin privileges")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Created new admin user '{username}'")
    
    print(f"\n✓ Admin credentials configured:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"\n✓ You can now access the admin panel at: http://127.0.0.1:8000/admin/")
except Exception as e:
    print(f"✗ Error creating admin user: {e}")

