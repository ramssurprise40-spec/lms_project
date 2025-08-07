from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import Course, UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ["user", "role", "bio"]


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "instructor"]
