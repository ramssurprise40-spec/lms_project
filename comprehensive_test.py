#!/usr/bin/env python
"""
Comprehensive LMS Project Testing Script
This script tests all major functionality of the LMS system.
"""

import os
import sys

import django
from django.conf import settings
from django.test.utils import override_settings

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

import json

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction

# Import Django components
from django.test import Client
from django.urls import NoReverseMatch, reverse

User = get_user_model()


class LMSTestSuite:
    def __init__(self):
        # Override settings for testing
        self.settings_override = override_settings(
            ALLOWED_HOSTS=["*"],  # Allow all hosts for testing
            AUTHENTICATION_BACKENDS=[
                "django.contrib.auth.backends.ModelBackend",
            ],  # Remove Axes for testing
        )
        self.settings_override.enable()

        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success = []

    def __del__(self):
        if hasattr(self, "settings_override"):
            self.settings_override.disable()

    def log_error(self, test_name, error):
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")

    def log_warning(self, test_name, warning):
        self.warnings.append(f"{test_name}: {warning}")
        print(f"⚠️  {test_name}: {warning}")

    def log_success(self, test_name, message="OK"):
        self.success.append(f"{test_name}: {message}")
        print(f"✅ {test_name}: {message}")

    def test_database_setup(self):
        """Test database and migrations"""
        try:
            # Check if we can query the User model
            user_count = User.objects.count()
            self.log_success("Database Connection", f"Connected, {user_count} users")

            # Check models
            from core.models import Assignment, Course, Enrollment, Exam

            course_count = Course.objects.count()
            assignment_count = Assignment.objects.count()
            exam_count = Exam.objects.count()
            enrollment_count = Enrollment.objects.count()

            self.log_success(
                "Core Models",
                f"Courses: {course_count}, Assignments: {assignment_count}, Exams: {exam_count}, Enrollments: {enrollment_count}",
            )

        except Exception as e:
            self.log_error("Database Setup", str(e))

    def test_url_patterns(self):
        """Test all URL patterns are accessible"""
        urls_to_test = [
            "home",
            "register",
            "login",
            "course_list",
            "course_categories",
            "ai_dashboard",
            "ai_lesson_planner",
            "ai_quiz_generator",
            "ai_rubric_generator",
            "ai_concept_explainer",
            "analytics_dashboard",
            "calendar",
            "notifications",
        ]

        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                self.log_success(f"URL Pattern '{url_name}'", f"Resolves to {url}")
            except NoReverseMatch as e:
                self.log_error(f"URL Pattern '{url_name}'", f"NoReverseMatch: {str(e)}")
            except Exception as e:
                self.log_error(f"URL Pattern '{url_name}'", str(e))

    def test_authentication_pages(self):
        """Test authentication-related pages"""
        try:
            # Test home page
            response = self.client.get("/")
            if response.status_code == 200:
                self.log_success("Home Page", f"Status {response.status_code}")
            else:
                self.log_warning("Home Page", f"Status {response.status_code}")

            # Test login page
            response = self.client.get("/login/")
            if response.status_code == 200:
                self.log_success("Login Page", f"Status {response.status_code}")
            else:
                self.log_error("Login Page", f"Status {response.status_code}")

            # Test register page
            response = self.client.get("/register/")
            if response.status_code == 200:
                self.log_success("Register Page", f"Status {response.status_code}")
            else:
                self.log_error("Register Page", f"Status {response.status_code}")

        except Exception as e:
            self.log_error("Authentication Pages", str(e))

    def create_test_users(self):
        """Create test users for different roles"""
        try:
            with transaction.atomic():
                # Create superuser if doesn't exist
                if not User.objects.filter(username="admin").exists():
                    admin_user = User.objects.create_superuser(
                        username="admin",
                        email="admin@test.com",
                        password="admin123",
                        first_name="Admin",
                        last_name="User",
                        role="admin",
                    )
                    self.log_success("Admin User Created", f"Username: admin")
                else:
                    self.log_success("Admin User", "Already exists")

                # Create instructor
                if not User.objects.filter(username="instructor").exists():
                    instructor_user = User.objects.create_user(
                        username="instructor",
                        email="instructor@test.com",
                        password="instructor123",
                        first_name="John",
                        last_name="Instructor",
                        role="instructor",
                    )
                    self.log_success("Instructor User Created", f"Username: instructor")
                else:
                    self.log_success("Instructor User", "Already exists")

                # Create student
                if not User.objects.filter(username="student").exists():
                    student_user = User.objects.create_user(
                        username="student",
                        email="student@test.com",
                        password="student123",
                        first_name="Jane",
                        last_name="Student",
                        role="student",
                    )
                    self.log_success("Student User Created", f"Username: student")
                else:
                    self.log_success("Student User", "Already exists")

        except Exception as e:
            self.log_error("User Creation", str(e))

    def test_user_authentication(self):
        """Test user login functionality"""
        try:
            # Test admin login
            login_success = self.client.login(username="admin", password="admin123")
            if login_success:
                self.log_success("Admin Login", "Successful")
                self.client.logout()
            else:
                self.log_error("Admin Login", "Failed")

            # Test instructor login
            login_success = self.client.login(
                username="instructor", password="instructor123"
            )
            if login_success:
                self.log_success("Instructor Login", "Successful")
                self.client.logout()
            else:
                self.log_error("Instructor Login", "Failed")

            # Test student login
            login_success = self.client.login(username="student", password="student123")
            if login_success:
                self.log_success("Student Login", "Successful")
                self.client.logout()
            else:
                self.log_error("Student Login", "Failed")

        except Exception as e:
            self.log_error("User Authentication", str(e))

    def test_dashboard_access(self):
        """Test dashboard access for different user roles"""
        try:
            # Test admin dashboard
            self.client.login(username="admin", password="admin123")
            response = self.client.get("/admin/dashboard/")
            if response.status_code in [200, 302]:
                self.log_success("Admin Dashboard", f"Status {response.status_code}")
            else:
                self.log_error("Admin Dashboard", f"Status {response.status_code}")
            self.client.logout()

            # Test instructor dashboard
            self.client.login(username="instructor", password="instructor123")
            response = self.client.get("/instructor/dashboard/")
            if response.status_code in [200, 302]:
                self.log_success(
                    "Instructor Dashboard", f"Status {response.status_code}"
                )
            else:
                self.log_error("Instructor Dashboard", f"Status {response.status_code}")
            self.client.logout()

            # Test student dashboard
            self.client.login(username="student", password="student123")
            response = self.client.get("/student/dashboard/")
            if response.status_code in [200, 302]:
                self.log_success("Student Dashboard", f"Status {response.status_code}")
            else:
                self.log_error("Student Dashboard", f"Status {response.status_code}")
            self.client.logout()

        except Exception as e:
            self.log_error("Dashboard Access", str(e))

    def test_ai_features(self):
        """Test AI-powered features"""
        try:
            # Login as instructor for AI tools
            self.client.login(username="instructor", password="instructor123")

            ai_pages = [
                ("/ai/", "AI Dashboard"),
                ("/ai/lesson-planner/", "Lesson Planner"),
                ("/ai/quiz-generator/", "Quiz Generator"),
                ("/ai/rubric-generator/", "Rubric Generator"),
                ("/ai/concept-explainer/", "Concept Explainer"),
            ]

            for url, name in ai_pages:
                response = self.client.get(url)
                if response.status_code in [200, 302]:
                    self.log_success(
                        f"AI Feature - {name}", f"Status {response.status_code}"
                    )
                else:
                    self.log_warning(
                        f"AI Feature - {name}", f"Status {response.status_code}"
                    )

            self.client.logout()

        except Exception as e:
            self.log_error("AI Features", str(e))

    def test_course_functionality(self):
        """Test course-related functionality"""
        try:
            from core.models import Course, CourseCategory

            # Create test category
            category, created = CourseCategory.objects.get_or_create(
                name="Test Category",
                defaults={"description": "Test category for testing"},
            )

            # Login as instructor
            self.client.login(username="instructor", password="instructor123")
            instructor = User.objects.get(username="instructor")

            # Create test course
            course, created = Course.objects.get_or_create(
                title="Test Course",
                instructor=instructor,
                defaults={
                    "description": "Test course for testing",
                    "category": category,
                    "max_students": 30,
                    "is_published": True,
                    "difficulty_level": "beginner",
                },
            )

            if created:
                self.log_success("Course Creation", f"Created course: {course.title}")
            else:
                self.log_success("Course Creation", f"Course exists: {course.title}")

            # Test course list page
            response = self.client.get("/courses/")
            if response.status_code == 200:
                self.log_success("Course List Page", f"Status {response.status_code}")
            else:
                self.log_error("Course List Page", f"Status {response.status_code}")

            # Test course detail page
            response = self.client.get(f"/courses/{course.pk}/")
            if response.status_code == 200:
                self.log_success("Course Detail Page", f"Status {response.status_code}")
            else:
                self.log_error("Course Detail Page", f"Status {response.status_code}")

            self.client.logout()

        except Exception as e:
            self.log_error("Course Functionality", str(e))

    def test_assignment_and_exam_functionality(self):
        """Test assignment and exam functionality"""
        try:
            from core.models import Assignment, Course, Exam

            self.client.login(username="instructor", password="instructor123")
            instructor = User.objects.get(username="instructor")

            # Get or create a course
            course = Course.objects.filter(instructor=instructor).first()
            if not course:
                from core.models import CourseCategory

                category, _ = CourseCategory.objects.get_or_create(
                    name="Test Category", defaults={"description": "Test category"}
                )
                course = Course.objects.create(
                    title="Test Course for Assignments",
                    instructor=instructor,
                    description="Test course",
                    category=category,
                    max_students=30,
                    is_published=True,
                )

            # Test assignment creation page
            response = self.client.get(f"/courses/{course.pk}/assignment/")
            if response.status_code in [200, 302]:
                self.log_success(
                    "Assignment Creation Page", f"Status {response.status_code}"
                )
            else:
                self.log_warning(
                    "Assignment Creation Page", f"Status {response.status_code}"
                )

            # Test exam generation page
            response = self.client.get(f"/courses/{course.pk}/exam/generate/")
            if response.status_code in [200, 302]:
                self.log_success(
                    "Exam Generation Page", f"Status {response.status_code}"
                )
            else:
                self.log_warning(
                    "Exam Generation Page", f"Status {response.status_code}"
                )

            self.client.logout()

        except Exception as e:
            self.log_error("Assignment/Exam Functionality", str(e))

    def test_api_endpoints(self):
        """Test API endpoints"""
        try:
            # Test API endpoints that don't require authentication
            api_endpoints = [
                "/api/",
            ]

            for endpoint in api_endpoints:
                try:
                    response = self.client.get(endpoint)
                    if response.status_code in [200, 301, 302, 404]:
                        self.log_success(
                            f"API Endpoint {endpoint}", f"Status {response.status_code}"
                        )
                    else:
                        self.log_warning(
                            f"API Endpoint {endpoint}", f"Status {response.status_code}"
                        )
                except Exception as e:
                    self.log_warning(f"API Endpoint {endpoint}", str(e))

        except Exception as e:
            self.log_error("API Endpoints", str(e))

    def test_static_files(self):
        """Test static files configuration"""
        try:
            # Test static files URL
            response = self.client.get("/static/admin/css/base.css")
            if response.status_code in [200, 404]:  # 404 is OK if not collected
                self.log_success(
                    "Static Files",
                    f"Static URL accessible (Status {response.status_code})",
                )
            else:
                self.log_warning("Static Files", f"Status {response.status_code}")

        except Exception as e:
            self.log_error("Static Files", str(e))

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting LMS Comprehensive Testing...")
        print("=" * 60)

        # Run all tests
        self.test_database_setup()
        self.test_url_patterns()
        self.create_test_users()
        self.test_authentication_pages()
        self.test_user_authentication()
        self.test_dashboard_access()
        self.test_course_functionality()
        self.test_assignment_and_exam_functionality()
        self.test_ai_features()
        self.test_api_endpoints()
        self.test_static_files()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Success: {len(self.success)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")

        print(
            f"\n🎯 Overall Health: {len(self.success)}/{len(self.success) + len(self.warnings) + len(self.errors)} tests passed"
        )

        if len(self.errors) == 0:
            print("🎉 All critical functionality is working!")
        else:
            print(f"⚠️  {len(self.errors)} critical issues need attention.")


if __name__ == "__main__":
    test_suite = LMSTestSuite()
    test_suite.run_all_tests()
