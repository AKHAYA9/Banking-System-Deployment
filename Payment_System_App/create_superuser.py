# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Payment_System.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Load superuser info from environment variables
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
loginid = os.environ.get("DJANGO_SUPERUSER_LOGINID")  # Must match your model

def create_superuser():
    if not all([username, email, password, loginid]):
        print("❌ Missing environment variables for superuser creation.")
        return

    try:
        user = User.objects.get(username=username)
        if user.is_superuser:
            print(f"✅ Superuser '{username}' already exists.")
        else:
            print(f"⚠ User '{username}' exists but is not a superuser. Updating...")
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"✅ User '{username}' promoted to superuser.")
    except User.DoesNotExist:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            loginid=loginid  # Required field
        )
        print(f"✅ Superuser '{username}' created successfully.")

if __name__ == "__main__":
    create_superuser()
