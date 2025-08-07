from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("profile/", views.profile_update_view, name="profile_update"),
    # Moodle-like feature URLs
    path("categories/", views.course_categories_view, name="course_categories"),
    path(
        "category/<int:category_id>/courses/",
        views.category_courses_view,
        name="category_courses",
    ),
    path(
        "course/<int:course_id>/materials/",
        views.course_materials_view,
        name="course_materials",
    ),
    path("material/<int:material_id>/", views.access_material, name="access_material"),
    path(
        "course/<int:course_id>/manage/",
        views.manage_course_content,
        name="manage_course_content",
    ),
    path(
        "course/<int:course_id>/remove/<int:material_id>/",
        views.remove_course_content,
        name="remove_course_content",
    ),
    path(
        "course/<int:course_id>/discussions/",
        views.course_discussions_view,
        name="course_discussions",
    ),
    path(
        "discussion/<int:discussion_id>/",
        views.discussion_detail_view,
        name="discussion_detail",
    ),
    path(
        "course/<int:course_id>/announcements/",
        views.course_announcements_view,
        name="course_announcements",
    ),
    path(
        "progress/<int:course_id>/",
        views.student_progress_view,
        name="student_progress",
    ),
    path("progress/", views.student_progress_view, name="student_progress_overview"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("gradebook/<int:course_id>/", views.gradebook_view, name="gradebook"),
    path(
        "assignment/<int:assignment_id>/submit/",
        views.assignment_submission_view,
        name="assignment_submission",
    ),
    path("analytics/", views.analytics_dashboard_view, name="analytics_dashboard"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("courses/<int:pk>/enroll/", views.enroll_in_course, name="enroll_course"),
    path(
        "courses/<int:course_pk>/assignment/",
        views.assignment_create,
        name="assignment_create",
    ),
    path(
        "courses/<int:course_pk>/exam/generate/",
        views.generate_exam_view,
        name="generate_exam",
    ),
    path("exam/<int:exam_pk>/submit/", views.submit_exam_view, name="submit_exam"),
    path(
        "instructor/exams/",
        views.instructor_exam_submissions,
        name="instructor_exam_submissions",
    ),
    path(
        "submission/<int:submission_pk>/review/",
        views.review_submission,
        name="review_submission",
    ),
    path("unauthorized/", views.UnauthorizedView.as_view(), name="unauthorized"),
    path(
        "admin/dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"
    ),
    path(
        "instructor/dashboard/",
        views.InstructorDashboardView.as_view(),
        name="instructor_dashboard",
    ),
    path(
        "student/dashboard/",
        views.StudentDashboardView.as_view(),
        name="student_dashboard",
    ),
    # AI-powered instructor tools
    path("ai/", views.ai_dashboard, name="ai_dashboard"),
    path("ai/lesson-planner/", views.ai_lesson_planner, name="ai_lesson_planner"),
    path("ai/quiz-generator/", views.ai_quiz_generator, name="ai_quiz_generator"),
    path("ai/quiz/create/", views.create_quiz_from_ai, name="create_quiz_from_ai"),
    path("ai/rubric-generator/", views.ai_rubric_generator, name="ai_rubric_generator"),
    path(
        "ai/concept-explainer/", views.ai_concept_explainer, name="ai_concept_explainer"
    ),
    path(
        "ai/syllabus-generator/",
        views.ai_syllabus_generator,
        name="ai_syllabus_generator",
    ),
    # Student functionality
    path("student/profile/", views.student_profile_view, name="student_profile"),
    path("student/quizzes/", views.student_quiz_list, name="student_quiz_list"),
    path(
        "student/quiz/<int:exam_pk>/",
        views.student_quiz_detail,
        name="student_quiz_detail",
    ),
    path(
        "student/message/<int:instructor_id>/",
        views.message_instructor,
        name="message_instructor",
    ),
    # Add missing URLs
    path("assignment/list/", views.assignment_list, name="assignment_list"),
    path("exam/submissions/", views.exam_submission_list, name="exam_submission_list"),
    # API URLs
    path("api/", include("core.api_urls")),
]
