# C:\Users\Ramat\Desktop\lms_project\core\api\urls.py

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .. import views  # Import views from the parent 'core' app

# DRF ViewSet Router Setup - MOVED FROM core/urls.py
router = DefaultRouter()
# Note: Removed 'api/' prefix from the register path as it's now handled by the include in lms_backend/urls.py
router.register(r"courses", views.CourseViewSet)
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"assignments", views.AssignmentViewSet, basename="assignment")
router.register(r"grades", views.GradeViewSet, basename="grade")

urlpatterns = [
    path("", include(router.urls)),  # This includes all the routes from the router
    # API-specific path - MOVED FROM core/urls.py
    path(
        "instructor-dashboard/",
        views.InstructorDashboardAPIView.as_view(),
        name="api_instructor_dashboard",
    ),
]
