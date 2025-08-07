from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User model with roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return self.username


# UserProfile for additional details
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    # Additional student information
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Academic information
    student_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    major = models.CharField(max_length=100, blank=True)
    year_of_study = models.CharField(max_length=20, blank=True)

    # Social links
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)

    # Preferences
    timezone = models.CharField(max_length=50, default="UTC")
    language_preference = models.CharField(max_length=10, default="en")
    email_notifications = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def full_address(self):
        parts = [self.address, self.city, self.country]
        return ", ".join([part for part in parts if part])


# Course model
class Course(models.Model):
    DIFFICULTY_LEVELS = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    category = models.ForeignKey(
        "CourseCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="courses",
    )
    difficulty_level = models.CharField(
        max_length=20, choices=DIFFICULTY_LEVELS, default="beginner"
    )
    duration_weeks = models.IntegerField(default=12)
    max_students = models.IntegerField(default=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def enrolled_count(self):
        return self.enrollments.count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_students


# Enrollment model
class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


# Assignment model
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    description = models.TextField()
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title


# Grade model
class Grade(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="grades"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grades"
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}: {self.score}"


# Exam model
class Exam(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    instructions = models.TextField(blank=True)
    generated_content = models.TextField(blank=True)  # Raw AI generated content
    time_limit = models.IntegerField(default=60)  # in minutes
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Question model for structured quiz questions
class Question(models.Model):
    QUESTION_TYPES = (
        ("multiple_choice", "Multiple Choice"),
        ("true_false", "True/False"),
        ("short_answer", "Short Answer"),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default="multiple_choice"
    )
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.exam.title} - Q{self.order}: {self.text[:50]}..."


# Choice model for multiple choice questions
class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.question.text[:30]}... - {self.text}"


# ExamSubmission model
class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answers = models.JSONField()  # This is the correct field name to match the form
    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username}'s submission for {self.exam.title}"


# Course Category for better organization
class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome icon class
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def get_full_path(self):
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


# Course Materials/Resources
class CourseMaterial(models.Model):
    MATERIAL_TYPES = (
        ("document", "Document"),
        ("video", "Video"),
        ("link", "External Link"),
        ("presentation", "Presentation"),
        ("audio", "Audio"),
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="materials"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(
        max_length=20, choices=MATERIAL_TYPES, default="document"
    )
    file = models.FileField(upload_to="course_materials/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    is_downloadable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# Assignment Submissions
class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ("submitted", "Submitted"),
        ("graded", "Graded"),
        ("returned", "Returned"),
    )

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )
    content = models.TextField()  # Written submission
    file = models.FileField(upload_to="assignment_submissions/", blank=True, null=True)
    rubric_score = models.JSONField(
        blank=True, null=True
    )  # Support detailed rubric score
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ["assignment", "student"]

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


# Discussion Forum
class Discussion(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="discussions"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# Discussion Posts/Replies
class DiscussionPost(models.Model):
    discussion = models.ForeignKey(
        Discussion, on_delete=models.CASCADE, related_name="posts"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} - {self.discussion.title}"


# Announcements
class Announcement(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="announcements"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# Progress Tracking
class StudentProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="student_progress"
    )
    materials_completed = models.ManyToManyField(CourseMaterial, blank=True)
    assignments_completed = models.ManyToManyField(Assignment, blank=True)
    exams_completed = models.ManyToManyField(Exam, blank=True)
    overall_progress = models.FloatField(default=0.0)  # Percentage
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["student", "course"]

    def __str__(self):
        return (
            f"{self.student.username} - {self.course.title} ({self.overall_progress}%)"
        )


# Calendar Events
class CalendarEvent(models.Model):
    EVENT_TYPES = (
        ("assignment", "Assignment Due"),
        ("exam", "Exam"),
        ("class", "Class Session"),
        ("holiday", "Holiday"),
        ("other", "Other"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="events", blank=True, null=True
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="other")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"


# Notifications
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("grade", "Grade Posted"),
        ("assignment", "New Assignment"),
        ("announcement", "Announcement"),
        ("message", "Message"),
        ("reminder", "Reminder"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="message"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
