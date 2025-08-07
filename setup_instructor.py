#!/usr/bin/env python
"""
Script to create an instructor account for testing AI features
"""
import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

from core.models import User, UserProfile


def create_instructor():
    # Check if instructor already exists
    if User.objects.filter(username="instructor_demo").exists():
        print("✅ Instructor account 'instructor_demo' already exists!")
        user = User.objects.get(username="instructor_demo")
    else:
        # Create instructor user
        user = User.objects.create_user(
            username="instructor_demo",
            email="instructor@example.com",
            password="demo123",
            first_name="John",
            last_name="Doe",
            role="instructor",
        )
        print("✅ Created instructor account: instructor_demo")

    # Create or get user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user, defaults={"bio": "Demo instructor for testing AI features"}
    )

    if created:
        print("✅ Created instructor profile")
    else:
        print("✅ Instructor profile already exists")

    print(
        f"""
    🎓 INSTRUCTOR LOGIN DETAILS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Username: instructor_demo
    Password: demo123
    Role: Instructor
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    🚀 Next Steps:
    1. Start the server: python manage.py runserver
    2. Go to: http://127.0.0.1:8000/login/
    3. Login with the credentials above
    4. Access AI Tools from the instructor dashboard
    """
    )


if __name__ == "__main__":
    create_instructor()
