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
loginid = os.environ.get("DJANGO_SUPERUSER_LOGINID")  # MUST match your model

if username and email and password and loginid:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            loginid=loginid  # Pass the required field
        )
        print("Superuser created")
    else:
        print("Superuser already exists")
else:
    print("Missing environment variables for superuser")
