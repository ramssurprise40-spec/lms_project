from django.test import Client, TestCase
from django.urls import reverse

from core.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            role="student",
        )
        self.client = Client()

    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "testpassword123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_fail(self):
        """Test failed login"""
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertIn(
            "Invalid username or password.",
            [m.message for m in response.context["messages"]],
        )
