# core/api_urls.py

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet)
router.register(r"enrollments", views.EnrollmentViewSet)
router.register(r"assignments", views.AssignmentViewSet)
router.register(r"grades", views.GradeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Additional API endpoints can be added here
]
