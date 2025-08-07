#!/usr/bin/env python
"""
Login Pages Verification Script
This script specifically tests and verifies the login functionality and pages.
"""

import os
import sys

import django
from django.conf import settings
from django.test.utils import override_settings

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

# Import Django components
from django.test import Client
from django.urls import reverse

from core.forms import CustomUserCreationForm

User = get_user_model()


class LoginVerificationSuite:
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
        self.results = []

    def __del__(self):
        if hasattr(self, "settings_override"):
            self.settings_override.disable()

    def log_result(self, test_name, status, message=""):
        status_icon = "✅" if status else "❌"
        self.results.append({"test": test_name, "status": status, "message": message})
        print(f"{status_icon} {test_name}: {message}")

    def test_login_page_accessibility(self):
        """Test if login page is accessible"""
        try:
            response = self.client.get("/login/")
            if response.status_code == 200:
                self.log_result(
                    "Login Page Accessibility",
                    True,
                    f"Status {response.status_code} - Page loads successfully",
                )
                return True
            else:
                self.log_result(
                    "Login Page Accessibility",
                    False,
                    f"Status {response.status_code} - Page not accessible",
                )
                return False
        except Exception as e:
            self.log_result("Login Page Accessibility", False, f"Exception: {str(e)}")
            return False

    def test_login_page_content(self):
        """Test login page content and form"""
        try:
            response = self.client.get("/login/")
            content = response.content.decode()

            # Check for essential elements
            required_elements = [
                'form method="post"',
                'name="username"',
                'name="password"',
                'type="submit"',
                "csrf_token",
                "Welcome Back",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)

            if not missing_elements:
                self.log_result(
                    "Login Page Content", True, "All required form elements present"
                )
                return True
            else:
                self.log_result(
                    "Login Page Content",
                    False,
                    f"Missing elements: {', '.join(missing_elements)}",
                )
                return False
        except Exception as e:
            self.log_result("Login Page Content", False, f"Exception: {str(e)}")
            return False

    def test_register_page_accessibility(self):
        """Test if register page is accessible"""
        try:
            response = self.client.get("/register/")
            if response.status_code == 200:
                self.log_result(
                    "Register Page Accessibility",
                    True,
                    f"Status {response.status_code} - Page loads successfully",
                )
                return True
            else:
                self.log_result(
                    "Register Page Accessibility",
                    False,
                    f"Status {response.status_code} - Page not accessible",
                )
                return False
        except Exception as e:
            self.log_result(
                "Register Page Accessibility", False, f"Exception: {str(e)}"
            )
            return False

    def test_register_page_content(self):
        """Test register page content and form"""
        try:
            response = self.client.get("/register/")
            content = response.content.decode()

            # Check for essential elements
            required_elements = [
                'form method="post"',
                'name="username"',
                'name="email"',
                'name="password1"',
                'name="password2"',
                'type="submit"',
                "csrf_token",
                "Create Your Account",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)

            if not missing_elements:
                self.log_result(
                    "Register Page Content", True, "All required form elements present"
                )
                return True
            else:
                self.log_result(
                    "Register Page Content",
                    False,
                    f"Missing elements: {', '.join(missing_elements)}",
                )
                return False
        except Exception as e:
            self.log_result("Register Page Content", False, f"Exception: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for login testing"""
        try:
            with transaction.atomic():
                if not User.objects.filter(username="testuser").exists():
                    test_user = User.objects.create_user(
                        username="testuser",
                        email="test@example.com",
                        password="testpass123",
                        first_name="Test",
                        last_name="User",
                        role="student",
                    )
                    self.log_result(
                        "Test User Creation", True, f"Created test user: testuser"
                    )
                    return True
                else:
                    self.log_result(
                        "Test User Creation", True, f"Test user already exists"
                    )
                    return True
        except Exception as e:
            self.log_result("Test User Creation", False, f"Exception: {str(e)}")
            return False

    def test_valid_login(self):
        """Test login with valid credentials"""
        try:
            # First ensure test user exists
            if not User.objects.filter(username="testuser").exists():
                self.create_test_user()

            login_data = {"username": "testuser", "password": "testpass123"}

            response = self.client.post("/login/", login_data, follow=True)

            # Check if login was successful (should redirect)
            if (
                response.status_code == 200
                and "dashboard" in response.redirect_chain[-1][0]
            ):
                self.log_result(
                    "Valid Login Test",
                    True,
                    "Login successful, redirected to dashboard",
                )
                self.client.logout()  # Logout for next tests
                return True
            elif response.status_code == 200:
                # Check if we're logged in by checking the user in session
                user = response.wsgi_request.user
                if user.is_authenticated:
                    self.log_result(
                        "Valid Login Test",
                        True,
                        f"Login successful, user: {user.username}",
                    )
                    self.client.logout()
                    return True
                else:
                    self.log_result(
                        "Valid Login Test",
                        False,
                        "Login failed - user not authenticated",
                    )
                    return False
            else:
                self.log_result(
                    "Valid Login Test",
                    False,
                    f"Unexpected status code: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_result("Valid Login Test", False, f"Exception: {str(e)}")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            login_data = {"username": "invaliduser", "password": "wrongpassword"}

            response = self.client.post("/login/", login_data)

            # Should return to login page with error
            if response.status_code == 200:
                content = response.content.decode()
                # Check for error message or form errors
                if (
                    "Invalid username or password" in content
                    or "error" in content.lower()
                ):
                    self.log_result(
                        "Invalid Login Test",
                        True,
                        "Correctly rejected invalid credentials",
                    )
                    return True
                else:
                    self.log_result(
                        "Invalid Login Test",
                        False,
                        "No error message displayed for invalid credentials",
                    )
                    return False
            else:
                self.log_result(
                    "Invalid Login Test",
                    False,
                    f"Unexpected status code: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_result("Invalid Login Test", False, f"Exception: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration process"""
        try:
            # Delete test user if exists to test fresh registration
            User.objects.filter(username="newuser").delete()

            registration_data = {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "newpass123!",
                "password2": "newpass123!",
                "role": "student",
            }

            response = self.client.post("/register/", registration_data, follow=True)

            # Check if registration was successful
            if User.objects.filter(username="newuser").exists():
                user = User.objects.get(username="newuser")
                self.log_result(
                    "User Registration Test",
                    True,
                    f"User created successfully: {user.username}",
                )
                return True
            else:
                content = response.content.decode()
                self.log_result(
                    "User Registration Test",
                    False,
                    f"Registration failed. Response: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_result("User Registration Test", False, f"Exception: {str(e)}")
            return False

    def test_logout_functionality(self):
        """Test logout functionality"""
        try:
            # First login
            self.client.login(username="testuser", password="testpass123")

            # Then logout
            response = self.client.get("/logout/", follow=True)

            # Check if redirected to login page
            if response.status_code == 200 and any(
                "login" in url for url, _ in response.redirect_chain
            ):
                self.log_result(
                    "Logout Functionality",
                    True,
                    "Logout successful, redirected to login",
                )
                return True
            else:
                self.log_result(
                    "Logout Functionality",
                    False,
                    f"Logout failed. Status: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_result("Logout Functionality", False, f"Exception: {str(e)}")
            return False

    def test_authentication_forms(self):
        """Test authentication forms"""
        try:
            # Test AuthenticationForm
            auth_form = AuthenticationForm()
            if (
                hasattr(auth_form, "fields")
                and "username" in auth_form.fields
                and "password" in auth_form.fields
            ):
                self.log_result(
                    "Authentication Form",
                    True,
                    "AuthenticationForm properly configured",
                )
            else:
                self.log_result(
                    "Authentication Form",
                    False,
                    "AuthenticationForm missing required fields",
                )
                return False

            # Test CustomUserCreationForm
            creation_form = CustomUserCreationForm()
            required_fields = ["username", "password1", "password2", "role"]
            missing_fields = [
                field for field in required_fields if field not in creation_form.fields
            ]

            if not missing_fields:
                self.log_result(
                    "User Creation Form",
                    True,
                    "CustomUserCreationForm properly configured",
                )
                return True
            else:
                self.log_result(
                    "User Creation Form",
                    False,
                    f"Missing fields: {', '.join(missing_fields)}",
                )
                return False

        except Exception as e:
            self.log_result("Authentication Forms", False, f"Exception: {str(e)}")
            return False

    def test_home_page_login_links(self):
        """Test login links on home page"""
        try:
            response = self.client.get("/")
            content = response.content.decode()

            # Check for login and register links
            has_login_link = (
                'href="/login/"' in content or "{% url 'login' %}" in content
            )
            has_register_link = (
                'href="/register/"' in content or "{% url 'register' %}" in content
            )

            if has_login_link and has_register_link:
                self.log_result(
                    "Home Page Login Links", True, "Login and register links present"
                )
                return True
            else:
                missing = []
                if not has_login_link:
                    missing.append("login link")
                if not has_register_link:
                    missing.append("register link")
                self.log_result(
                    "Home Page Login Links", False, f"Missing: {', '.join(missing)}"
                )
                return False

        except Exception as e:
            self.log_result("Home Page Login Links", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all login page verification tests"""
        print("🔐 Starting Login Pages Verification...")
        print("=" * 60)

        # Run all tests
        tests = [
            self.test_login_page_accessibility,
            self.test_login_page_content,
            self.test_register_page_accessibility,
            self.test_register_page_content,
            self.create_test_user,
            self.test_valid_login,
            self.test_invalid_login,
            self.test_user_registration,
            self.test_logout_functionality,
            self.test_authentication_forms,
            self.test_home_page_login_links,
        ]

        for test in tests:
            test()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 LOGIN VERIFICATION SUMMARY")
        print("=" * 60)

        passed = sum(1 for result in self.results if result["status"])
        total = len(self.results)

        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {total - passed}")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%")

        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["status"]:
                    print(f"  - {result['test']}: {result['message']}")

        print(
            f"\n🎯 Overall Login System Health: {'EXCELLENT' if passed/total >= 0.8 else 'GOOD' if passed/total >= 0.6 else 'NEEDS ATTENTION'}"
        )

        if passed == total:
            print("🎉 All login functionality is working perfectly!")
        else:
            print(f"⚠️  {total - passed} issues found in login system.")


if __name__ == "__main__":
    verification = LoginVerificationSuite()
    verification.run_all_tests()
