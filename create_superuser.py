# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Payment_System.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
loginid = os.environ.get("DJANGO_SUPERUSER_LOGINID")  # Your custom required field


def create_superuser():
    if not all([username, email, password, loginid]):
        print("❌ Missing environment variables for superuser creation.")
        return

    # Get all users with this username
    existing_users = User.objects.filter(username=username)

    # If duplicates exist, remove them
    if existing_users.count() > 1:
        print(f"⚠ Found {existing_users.count()} duplicates. Deleting all duplicates...")
        existing_users.delete()

    # If only one exists
    elif existing_users.count() == 1:
        user = existing_users.first()
        if user.is_superuser:
            print(f"✅ Superuser '{username}' already exists.")
            return
        else:
            print(f"⚠ User '{username}' exists but is not a superuser. Promoting...")
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"✅ User '{username}' promoted to superuser.")
            return

    # If no user exists → create fresh superuser
    print(f"➕ Creating new superuser '{username}'...")
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        loginid=loginid
    )
    print(f"✅ Superuser '{username}' created successfully.")


if __name__ == "__main__":
    create_superuser()
