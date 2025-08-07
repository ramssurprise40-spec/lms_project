from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import (
    Announcement,
    CalendarEvent,
    Course,
    CourseCategory,
    CourseMaterial,
    Discussion,
    Enrollment,
    Notification,
    UserProfile,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create test data for the LMS"

    def handle(self, *args, **options):
        # Create test instructor
        instructor, created = User.objects.get_or_create(
            username="instructor",
            defaults={
                "email": "instructor@test.com",
                "first_name": "John",
                "last_name": "Instructor",
                "role": "instructor",
            },
        )
        if created:
            instructor.set_password("password123")
            instructor.save()
            UserProfile.objects.create(user=instructor, bio="Test instructor profile")
            self.stdout.write(f"Created instructor: {instructor.username}")

        # Create test student
        student, created = User.objects.get_or_create(
            username="student",
            defaults={
                "email": "student@test.com",
                "first_name": "Jane",
                "last_name": "Student",
                "role": "student",
            },
        )
        if created:
            student.set_password("password123")
            student.save()
            UserProfile.objects.create(user=student, bio="Test student profile")
            self.stdout.write(f"Created student: {student.username}")

        # Create test courses
        for i in range(3):
            course, created = Course.objects.get_or_create(
                title=f"Test Course {i+1}",
                defaults={
                    "description": f"This is test course {i+1} description",
                    "instructor": instructor,
                    "difficulty_level": "beginner",
                    "price": 99.99,
                    "is_published": True,
                },
            )
            if created:
                self.stdout.write(f"Created course: {course.title}")

                # Enroll student in courses
                Enrollment.objects.get_or_create(student=student, course=course)

        # Create course categories
        categories = [
            ("Programming", "fas fa-code"),
            ("Mathematics", "fas fa-calculator"),
            ("Science", "fas fa-flask"),
            ("Business", "fas fa-briefcase"),
        ]

        for cat_name, icon in categories:
            category, created = CourseCategory.objects.get_or_create(
                name=cat_name,
                defaults={"icon": icon, "description": f"{cat_name} courses"},
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Add categories to courses
        programming_cat = CourseCategory.objects.get(name="Programming")
        Course.objects.filter(title__contains="Course 1").update(
            category=programming_cat
        )

        # Create course materials
        courses = Course.objects.all()[:2]  # First 2 courses
        for course in courses:
            for i in range(3):
                material, created = CourseMaterial.objects.get_or_create(
                    course=course,
                    title=f"Lesson {i+1} Material",
                    defaults={
                        "description": f"Learning material for lesson {i+1}",
                        "material_type": "document",
                        "order": i,
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created material: {material.title} for {course.title}"
                    )

        # Create discussions
        for course in courses:
            discussion, created = Discussion.objects.get_or_create(
                course=course,
                title="General Discussion",
                defaults={
                    "description": "General discussion for the course",
                    "created_by": instructor,
                },
            )
            if created:
                self.stdout.write(
                    f"Created discussion: {discussion.title} for {course.title}"
                )

        # Create announcements
        for course in courses:
            announcement, created = Announcement.objects.get_or_create(
                course=course,
                title="Welcome to the Course!",
                defaults={
                    "content": "Welcome to our course! Please read the syllabus and get started.",
                    "created_by": instructor,
                },
            )
            if created:
                self.stdout.write(
                    f"Created announcement: {announcement.title} for {course.title}"
                )

        # Create calendar events
        today = datetime.now().date()
        for i, course in enumerate(courses):
            event, created = CalendarEvent.objects.get_or_create(
                title=f"{course.title} - Midterm Exam",
                defaults={
                    "description": f"Midterm examination for {course.title}",
                    "course": course,
                    "event_type": "exam",
                    "start_date": datetime.combine(
                        today + timedelta(days=14 + i * 7), datetime.min.time()
                    ),
                    "created_by": instructor,
                },
            )
            if created:
                self.stdout.write(f"Created calendar event: {event.title}")

        # Create notifications
        notification, created = Notification.objects.get_or_create(
            recipient=student,
            title="Welcome to the LMS!",
            defaults={
                "message": "Welcome to our Learning Management System. Explore your courses and start learning!",
                "notification_type": "message",
            },
        )
        if created:
            self.stdout.write(f"Created notification for {student.username}")

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created test data with Moodle-like features!"
            )
        )
        self.stdout.write("Login credentials:")
        self.stdout.write("  Instructor: instructor / password123")
        self.stdout.write("  Student: student / password123")
        self.stdout.write("  Admin: bukasa / (your admin password)")
