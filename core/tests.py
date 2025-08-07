from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient

from .models import Choice, Course, Enrollment, Exam, Question

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="testinstructor", password="testpass123", role="instructor"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="A course for testing",
            instructor=self.instructor,
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, "Test Course")
        self.assertEqual(self.course.instructor.username, "testinstructor")

    def test_course_str_method(self):
        self.assertEqual(str(self.course), "Test Course")


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="testinstructor", password="testpass123", role="instructor"
        )
        self.student = User.objects.create_user(
            username="teststudent", password="testpass123", role="student"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="A course for testing",
            instructor=self.instructor,
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course
        )

    def test_enrollment_creation(self):
        self.assertEqual(self.enrollment.student.username, "teststudent")
        self.assertEqual(self.enrollment.course.title, "Test Course")

    def test_course_enrolled_count(self):
        self.assertEqual(self.course.enrolled_count, 1)


class ExamModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="testinstructor", password="testpass123", role="instructor"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="A course for testing",
            instructor=self.instructor,
        )
        self.exam = Exam.objects.create(
            title="Test Exam", course=self.course, created_by=self.instructor
        )
        self.question = Question.objects.create(
            exam=self.exam, text="What is 2 + 2?", question_type="multiple_choice"
        )
        self.choice1 = Choice.objects.create(
            question=self.question, text="3", is_correct=False
        )
        self.choice2 = Choice.objects.create(
            question=self.question, text="4", is_correct=True
        )

    def test_exam_and_question_creation(self):
        self.assertEqual(self.exam.title, "Test Exam")
        self.assertEqual(self.question.text, "What is 2 + 2?")
        self.assertEqual(self.question.choices.count(), 2)
        self.assertEqual(
            self.question.choices.filter(is_correct=True).first().text, "4"
        )

    def test_exam_str_method(self):
        self.assertEqual(str(self.exam), "Test Exam")
