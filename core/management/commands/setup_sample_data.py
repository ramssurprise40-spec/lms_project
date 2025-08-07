from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Course, Enrollment, Exam, User, UserProfile


class Command(BaseCommand):
    help = "Set up sample data for the LMS"

    def handle(self, *args, **options):
        User = get_user_model()

        # Create sample users
        instructor, created = User.objects.get_or_create(
            username="instructor1",
            defaults={
                "first_name": "John",
                "last_name": "Smith",
                "email": "instructor@edukart.edu",
                "role": "instructor",
            },
        )
        if created:
            instructor.set_password("password123")
            instructor.save()
            UserProfile.objects.create(
                user=instructor, bio="Experienced educator with 10 years of teaching."
            )
            self.stdout.write(self.style.SUCCESS("Created instructor: instructor1"))

        student, created = User.objects.get_or_create(
            username="student1",
            defaults={
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "student@edukart.edu",
                "role": "student",
            },
        )
        if created:
            student.set_password("password123")
            student.save()
            UserProfile.objects.create(
                user=student, bio="Eager to learn new skills and advance my career."
            )
            self.stdout.write(self.style.SUCCESS("Created student: student1"))

        # Create sample courses
        course1, created = Course.objects.get_or_create(
            title="Introduction to Computer Science",
            defaults={
                "description": "A comprehensive introduction to computer science fundamentals including programming, algorithms, and data structures.",
                "instructor": instructor,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created course: Introduction to Computer Science")
            )

        course2, created = Course.objects.get_or_create(
            title="Web Development Fundamentals",
            defaults={
                "description": "Learn the basics of web development including HTML, CSS, JavaScript, and modern frameworks.",
                "instructor": instructor,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created course: Web Development Fundamentals")
            )

        course3, created = Course.objects.get_or_create(
            title="Data Science Essentials",
            defaults={
                "description": "Master data analysis, visualization, and machine learning fundamentals using Python.",
                "instructor": instructor,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created course: Data Science Essentials")
            )

        # Enroll student in courses
        enrollment1, created = Enrollment.objects.get_or_create(
            student=student, course=course1
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Enrolled student in Introduction to Computer Science"
                )
            )

        enrollment2, created = Enrollment.objects.get_or_create(
            student=student, course=course2
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Enrolled student in Web Development Fundamentals")
            )

        # Create sample exams
        exam1, created = Exam.objects.get_or_create(
            title="Computer Science Basics Quiz",
            defaults={"course": course1, "created_by": instructor},
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created exam: Computer Science Basics Quiz")
            )

        exam2, created = Exam.objects.get_or_create(
            title="HTML & CSS Assessment",
            defaults={"course": course2, "created_by": instructor},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created exam: HTML & CSS Assessment"))

        self.stdout.write(
            self.style.SUCCESS("Sample data setup completed successfully!")
        )
        self.stdout.write("Login credentials:")
        self.stdout.write("Instructor - Username: instructor1, Password: password123")
        self.stdout.write("Student - Username: student1, Password: password123")
