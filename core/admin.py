from django.contrib import admin

from .models import (
    Announcement,
    Assignment,
    AssignmentSubmission,
    CalendarEvent,
    Choice,
    Course,
    CourseCategory,
    CourseMaterial,
    Discussion,
    DiscussionPost,
    Enrollment,
    Exam,
    ExamSubmission,
    Grade,
    Notification,
    Question,
    StudentProgress,
    User,
    UserProfile,
)


# User Management
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name", "role", "is_active"]
    list_filter = ["role", "is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "get_role", "bio"]
    search_fields = ["user__username", "bio"]

    def get_role(self, obj):
        return obj.user.role

    get_role.short_description = "Role"


# Course Management
@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    search_fields = ["name"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "instructor",
        "category",
        "difficulty_level",
        "enrolled_count",
        "max_students",
        "is_published",
    ]
    list_filter = ["category", "difficulty_level", "is_published", "created_at"]
    search_fields = ["title", "description", "instructor__username"]
    readonly_fields = ["enrolled_count"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "enrolled_at"]
    list_filter = ["enrolled_at", "course"]
    search_fields = ["student__username", "course__title"]


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "material_type", "order", "is_downloadable"]
    list_filter = ["material_type", "is_downloadable", "course"]
    search_fields = ["title", "course__title"]


# Assignment Management
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "due_date"]
    list_filter = ["due_date", "course"]
    search_fields = ["title", "course__title"]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ["assignment", "student", "status", "grade", "submitted_at"]
    list_filter = ["status", "submitted_at", "assignment"]
    search_fields = ["student__username", "assignment__title"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student", "assignment", "score", "graded_at"]
    list_filter = ["graded_at", "assignment"]
    search_fields = ["student__username", "assignment__title"]


# Exam Management
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "created_by", "time_limit", "is_published"]
    list_filter = ["is_published", "created_at", "course"]
    search_fields = ["title", "course__title"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["exam", "question_type", "order", "points"]
    list_filter = ["question_type", "exam"]
    search_fields = ["text", "exam__title"]
    ordering = ["exam", "order"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["question", "text", "is_correct", "order"]
    list_filter = ["is_correct", "question__exam"]
    search_fields = ["text", "question__text"]
    ordering = ["question", "order"]


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = ["exam", "student", "grade", "submitted_at", "graded_at"]
    list_filter = ["submitted_at", "graded_at", "exam"]
    search_fields = ["student__username", "exam__title"]


# Discussion Management
@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "created_by", "is_pinned", "created_at"]
    list_filter = ["is_pinned", "created_at", "course"]
    search_fields = ["title", "course__title"]


@admin.register(DiscussionPost)
class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ["discussion", "author", "created_at", "parent"]
    list_filter = ["created_at", "discussion"]
    search_fields = ["content", "author__username"]


# Communication
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "created_by", "is_urgent", "created_at"]
    list_filter = ["is_urgent", "created_at", "course"]
    search_fields = ["title", "content", "course__title"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "title", "notification_type", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["recipient__username", "title", "message"]


# Progress and Calendar
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "overall_progress", "last_accessed"]
    list_filter = ["course", "last_accessed"]
    search_fields = ["student__username", "course__title"]


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "event_type", "start_date", "created_by"]
    list_filter = ["event_type", "start_date", "course"]
    search_fields = ["title", "description", "course__title"]
