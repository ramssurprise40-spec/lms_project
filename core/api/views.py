from rest_framework import permissions, viewsets

from core.api.serializers import CourseSerializer, UserProfileSerializer
from core.models import Course, UserProfile


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
