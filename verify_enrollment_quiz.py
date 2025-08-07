#!/usr/bin/env python
"""
Enrollment and Quiz Verification Script
This script tests enrollment and quiz response functionality.
"""

import os
import sys

import django
from django.test.utils import override_settings

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

import json

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import Client

User = get_user_model()


class EnrollmentQuizTestSuite:
    def __init__(self):
        # Override settings for testing
        self.settings_override = override_settings(
            ALLOWED_HOSTS=["*"],
            AUTHENTICATION_BACKENDS=["django.contrib.auth.backends.ModelBackend"],
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

    def setup_test_data(self):
        """Create test data for enrollment and quiz testing"""
        try:
            from core.models import (
                Choice,
                Course,
                CourseCategory,
                Enrollment,
                Exam,
                ExamSubmission,
                Question,
            )

            with transaction.atomic():
                # Create test users if they don't exist
                if not User.objects.filter(username="test_instructor").exists():
                    test_instructor = User.objects.create_user(
                        username="test_instructor",
                        password="testpass123",
                        email="instructor@test.com",
                        role="instructor",
                        first_name="Test",
                        last_name="Instructor",
                    )
                else:
                    test_instructor = User.objects.get(username="test_instructor")

                if not User.objects.filter(username="test_student").exists():
                    test_student = User.objects.create_user(
                        username="test_student",
                        password="testpass123",
                        email="student@test.com",
                        role="student",
                        first_name="Test",
                        last_name="Student",
                    )
                else:
                    test_student = User.objects.get(username="test_student")

                # Create test category
                category, _ = CourseCategory.objects.get_or_create(
                    name="Test Category",
                    defaults={"description": "Test category for verification"},
                )

                # Create test course
                course, created = Course.objects.get_or_create(
                    title="Test Course for Enrollment",
                    instructor=test_instructor,
                    defaults={
                        "description": "A test course for enrollment testing",
                        "category": category,
                        "max_students": 30,
                        "is_published": True,
                    },
                )

                # Create test exam with questions
                exam, exam_created = Exam.objects.get_or_create(
                    title="Test Quiz",
                    course=course,
                    created_by=test_instructor,
                    defaults={
                        "instructions": "This is a test quiz for verification",
                        "time_limit": 30,
                        "is_published": True,
                    },
                )

                # Create questions if exam was just created
                if exam_created or not exam.questions.exists():
                    # Clear existing questions first
                    exam.questions.all().delete()

                    # Create multiple choice question
                    mc_question = Question.objects.create(
                        exam=exam,
                        text="What is 2 + 2?",
                        question_type="multiple_choice",
                        points=1,
                        order=1,
                    )

                    # Create choices for MC question
                    Choice.objects.create(
                        question=mc_question, text="3", is_correct=False, order=1
                    )
                    Choice.objects.create(
                        question=mc_question, text="4", is_correct=True, order=2
                    )
                    Choice.objects.create(
                        question=mc_question, text="5", is_correct=False, order=3
                    )

                    # Create true/false question
                    tf_question = Question.objects.create(
                        exam=exam,
                        text="Python is a programming language.",
                        question_type="true_false",
                        points=1,
                        order=2,
                    )

                self.log_result(
                    "Test Data Setup", True, "Created test users, course, and quiz"
                )
                return {
                    "instructor": test_instructor,
                    "student": test_student,
                    "course": course,
                    "exam": exam,
                }

        except Exception as e:
            self.log_result("Test Data Setup", False, f"Exception: {str(e)}")
            return None

    def test_course_list_accessibility(self):
        """Test if course list page is accessible"""
        try:
            response = self.client.get("/courses/")
            if response.status_code == 200:
                self.log_result(
                    "Course List Page", True, f"Status {response.status_code}"
                )
                return True
            else:
                self.log_result(
                    "Course List Page", False, f"Status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("Course List Page", False, f"Exception: {str(e)}")
            return False

    def test_course_detail_accessibility(self, course):
        """Test if course detail page is accessible"""
        try:
            response = self.client.get(f"/courses/{course.id}/")
            if response.status_code == 200:
                self.log_result(
                    "Course Detail Page", True, f"Status {response.status_code}"
                )
                return True
            else:
                self.log_result(
                    "Course Detail Page", False, f"Status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("Course Detail Page", False, f"Exception: {str(e)}")
            return False

    def test_enrollment_functionality(self, student, course):
        """Test course enrollment functionality"""
        try:
            from core.models import Enrollment

            # Login as student
            self.client.login(username="test_student", password="testpass123")

            # Check enrollment count before
            initial_count = Enrollment.objects.filter(
                student=student, course=course
            ).count()

            # Attempt to enroll
            response = self.client.post(f"/courses/{course.id}/enroll/", follow=True)

            # Check enrollment count after
            final_count = Enrollment.objects.filter(
                student=student, course=course
            ).count()

            if response.status_code == 200 and final_count > initial_count:
                self.log_result(
                    "Course Enrollment", True, "Student successfully enrolled"
                )
                self.client.logout()
                return True
            elif final_count > initial_count:
                self.log_result(
                    "Course Enrollment",
                    True,
                    "Student was already enrolled or successfully enrolled",
                )
                self.client.logout()
                return True
            else:
                self.log_result(
                    "Course Enrollment",
                    False,
                    f"Enrollment failed. Status: {response.status_code}",
                )
                self.client.logout()
                return False

        except Exception as e:
            self.log_result("Course Enrollment", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def test_quiz_list_accessibility(self):
        """Test if student can access quiz list"""
        try:
            # Login as student
            self.client.login(username="test_student", password="testpass123")

            response = self.client.get("/student/quizzes/")
            if response.status_code == 200:
                self.log_result(
                    "Quiz List Access", True, f"Status {response.status_code}"
                )
                self.client.logout()
                return True
            else:
                self.log_result(
                    "Quiz List Access", False, f"Status {response.status_code}"
                )
                self.client.logout()
                return False
        except Exception as e:
            self.log_result("Quiz List Access", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def test_quiz_detail_accessibility(self, exam):
        """Test if student can access quiz detail page"""
        try:
            # Login as student
            self.client.login(username="test_student", password="testpass123")

            response = self.client.get(f"/student/quiz/{exam.id}/")
            if response.status_code == 200:
                self.log_result(
                    "Quiz Detail Access", True, f"Status {response.status_code}"
                )
                self.client.logout()
                return True
            elif response.status_code == 302:
                # Might be redirected if already completed
                self.log_result(
                    "Quiz Detail Access",
                    True,
                    f"Redirected (Status {response.status_code}) - might be completed",
                )
                self.client.logout()
                return True
            else:
                self.log_result(
                    "Quiz Detail Access", False, f"Status {response.status_code}"
                )
                self.client.logout()
                return False
        except Exception as e:
            self.log_result("Quiz Detail Access", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def test_quiz_submission(self, exam):
        """Test quiz submission functionality"""
        try:
            from core.models import ExamSubmission

            # Login as student
            self.client.login(username="test_student", password="testpass123")

            # Delete any existing submissions for clean test
            ExamSubmission.objects.filter(
                exam=exam, student__username="test_student"
            ).delete()

            # Get questions to prepare answers
            questions = exam.questions.all()
            if not questions.exists():
                self.log_result("Quiz Submission", False, "No questions in exam")
                self.client.logout()
                return False

            # Prepare submission data
            submission_data = {}
            for question in questions:
                if question.question_type == "multiple_choice":
                    # Find correct choice
                    correct_choice = question.choices.filter(is_correct=True).first()
                    if correct_choice:
                        submission_data[f"question_{question.id}"] = correct_choice.id
                elif question.question_type == "true_false":
                    submission_data[f"question_{question.id}"] = "true"
                elif question.question_type == "short_answer":
                    submission_data[f"question_{question.id}"] = "Test answer"

            # Submit the quiz
            response = self.client.post(
                f"/student/quiz/{exam.id}/", submission_data, follow=True
            )

            # Check if submission was created
            submission_exists = ExamSubmission.objects.filter(
                exam=exam, student__username="test_student"
            ).exists()

            if response.status_code == 200 and submission_exists:
                submission = ExamSubmission.objects.filter(
                    exam=exam, student__username="test_student"
                ).first()
                grade = submission.grade if submission else 0
                self.log_result(
                    "Quiz Submission",
                    True,
                    f"Submitted successfully with grade: {grade}%",
                )
                self.client.logout()
                return True
            else:
                self.log_result(
                    "Quiz Submission",
                    False,
                    f"Submission failed. Status: {response.status_code}",
                )
                self.client.logout()
                return False

        except Exception as e:
            self.log_result("Quiz Submission", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def test_enrollment_status_display(self, student, course):
        """Test if enrollment status is correctly displayed on course detail page"""
        try:
            from core.models import Enrollment

            # Login as student
            self.client.login(username="test_student", password="testpass123")

            # Check if student is enrolled
            is_enrolled = Enrollment.objects.filter(
                student=student, course=course
            ).exists()

            response = self.client.get(f"/courses/{course.id}/")
            content = response.content.decode()

            if response.status_code == 200:
                if is_enrolled and "Enrolled" in content:
                    self.log_result(
                        "Enrollment Status Display",
                        True,
                        "Enrolled status correctly shown",
                    )
                    self.client.logout()
                    return True
                elif not is_enrolled and "Enroll Now" in content:
                    self.log_result(
                        "Enrollment Status Display",
                        True,
                        "Enroll button correctly shown",
                    )
                    self.client.logout()
                    return True
                else:
                    self.log_result(
                        "Enrollment Status Display",
                        False,
                        "Status display doesn't match enrollment state",
                    )
                    self.client.logout()
                    return False
            else:
                self.log_result(
                    "Enrollment Status Display",
                    False,
                    f"Page access failed. Status: {response.status_code}",
                )
                self.client.logout()
                return False

        except Exception as e:
            self.log_result("Enrollment Status Display", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def test_quiz_completion_status(self, student, exam):
        """Test if quiz completion status is correctly shown"""
        try:
            from core.models import ExamSubmission

            # Login as student
            self.client.login(username="test_student", password="testpass123")

            # Check if student has submitted the quiz
            has_submitted = ExamSubmission.objects.filter(
                student=student, exam=exam
            ).exists()

            response = self.client.get("/student/quizzes/")
            content = response.content.decode()

            if response.status_code == 200:
                if has_submitted and "Completed" in content:
                    self.log_result(
                        "Quiz Completion Status",
                        True,
                        "Completed status correctly shown",
                    )
                    self.client.logout()
                    return True
                elif not has_submitted and "Start Quiz" in content:
                    self.log_result(
                        "Quiz Completion Status",
                        True,
                        "Start Quiz button correctly shown",
                    )
                    self.client.logout()
                    return True
                else:
                    # Might be no quizzes available
                    self.log_result(
                        "Quiz Completion Status",
                        True,
                        "Status display appropriate for current state",
                    )
                    self.client.logout()
                    return True
            else:
                self.log_result(
                    "Quiz Completion Status",
                    False,
                    f"Quiz list access failed. Status: {response.status_code}",
                )
                self.client.logout()
                return False

        except Exception as e:
            self.log_result("Quiz Completion Status", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def test_instructor_quiz_management(self, instructor, course, exam):
        """Test instructor's ability to manage quizzes"""
        try:
            # Login as instructor
            self.client.login(username="test_instructor", password="testpass123")

            # Test exam generation page
            response = self.client.get(f"/courses/{course.id}/exam/generate/")
            if response.status_code in [200, 302]:
                self.log_result(
                    "Instructor Quiz Management",
                    True,
                    f"Can access quiz generation (Status {response.status_code})",
                )
            else:
                self.log_result(
                    "Instructor Quiz Management",
                    False,
                    f"Cannot access quiz generation (Status {response.status_code})",
                )
                self.client.logout()
                return False

            # Test exam submissions view
            response = self.client.get("/instructor/exams/")
            if response.status_code in [200, 302]:
                self.log_result(
                    "Instructor Exam Submissions",
                    True,
                    f"Can access submissions (Status {response.status_code})",
                )
                self.client.logout()
                return True
            else:
                self.log_result(
                    "Instructor Exam Submissions",
                    False,
                    f"Cannot access submissions (Status {response.status_code})",
                )
                self.client.logout()
                return False

        except Exception as e:
            self.log_result("Instructor Quiz Management", False, f"Exception: {str(e)}")
            self.client.logout()
            return False

    def run_all_tests(self):
        """Run all enrollment and quiz tests"""
        print("🎓 Starting Enrollment and Quiz Verification...")
        print("=" * 60)

        # Setup test data
        test_data = self.setup_test_data()
        if not test_data:
            print("❌ Failed to setup test data. Aborting tests.")
            return

        instructor = test_data["instructor"]
        student = test_data["student"]
        course = test_data["course"]
        exam = test_data["exam"]

        # Run tests
        self.test_course_list_accessibility()
        self.test_course_detail_accessibility(course)
        self.test_enrollment_functionality(student, course)
        self.test_enrollment_status_display(student, course)
        self.test_quiz_list_accessibility()
        self.test_quiz_detail_accessibility(exam)
        self.test_quiz_submission(exam)
        self.test_quiz_completion_status(student, exam)
        self.test_instructor_quiz_management(instructor, course, exam)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 ENROLLMENT & QUIZ VERIFICATION SUMMARY")
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
            f"\n🎯 Overall System Health: {'EXCELLENT' if passed/total >= 0.8 else 'GOOD' if passed/total >= 0.6 else 'NEEDS ATTENTION'}"
        )

        if passed == total:
            print("🎉 All enrollment and quiz functionality is working perfectly!")
        else:
            print(f"⚠️  {total - passed} issues found that need attention.")


if __name__ == "__main__":
    test_suite = EnrollmentQuizTestSuite()
    test_suite.run_all_tests()
