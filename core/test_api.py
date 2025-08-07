# Fichier: core/test_api.py

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Choice, Course, Enrollment, Exam, Question

User = get_user_model()


class APITest(APITestCase):
    def setUp(self):
        """Set up the necessary objects for the tests."""
        self.client = APIClient()

        # Create users with different roles
        self.admin = User.objects.create_superuser(
            "admin", "admin@example.com", "password123"
        )
        self.instructor = User.objects.create_user(
            "instructor", "instructor@example.com", "password123", role="instructor"
        )
        self.student = User.objects.create_user(
            "student", "student@example.com", "password123", role="student"
        )

        # Create a course
        self.course = Course.objects.create(
            title="Test Course API",
            description="Test Course Description",
            instructor=self.instructor,
        )

        # Create an exam for the course
        self.exam = Exam.objects.create(
            title="Test Exam", course=self.course, created_by=self.instructor
        )
        self.question = Question.objects.create(
            exam=self.exam, text="Sample question", question_type="multiple_choice"
        )
        Choice.objects.create(
            question=self.question, text="Correct answer", is_correct=True
        )
        Choice.objects.create(
            question=self.question, text="Wrong answer", is_correct=False
        )

        # URLS (using DRF router naming convention)
        self.course_list_url = reverse("course-list")
        self.course_detail_url = reverse("course-detail", kwargs={"pk": self.course.pk})

    def test_unauthenticated_access_to_courses(self):
        """Ensure unauthenticated users cannot access course API."""
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_can_list_courses(self):
        """Ensure authenticated students can list courses."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_cannot_create_course(self):
        """Ensure students cannot create a course."""
        self.client.force_authenticate(user=self.student)
        data = {
            "title": "New Course by Student",
            "description": "Description",
            "instructor": self.instructor.pk,
        }
        response = self.client.post(self.course_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_create_course(self):
        """Ensure instructors can create a course."""
        self.client.force_authenticate(user=self.instructor)
        data = {
            "title": "New Course by Instructor",
            "description": "Course created by an instructor",
        }
        response = self.client.post(self.course_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_instructor_can_update_own_course(self):
        """Ensure instructors can update their own course."""
        self.client.force_authenticate(user=self.instructor)
        data = {"title": "Updated Course Title"}
        response = self.client.patch(self.course_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated Course Title")

    def test_instructor_cannot_update_other_instructor_course(self):
        """Ensure instructors cannot update courses they do not own."""
        other_instructor = User.objects.create_user(
            "other_instructor", "other@example.com", "password123", role="instructor"
        )
        self.client.force_authenticate(user=other_instructor)
        data = {"title": "Malicious Update"}
        response = self.client.patch(self.course_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_course(self):
        """Ensure admin users can delete any course."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)
