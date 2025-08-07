from rest_framework import serializers

from .models import Assignment, Course, Enrollment, Grade, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "instructor", "created_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "enrolled_at"]


class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ["id", "course", "title", "description", "due_date"]


class GradeSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = ["id", "assignment", "student", "score", "feedback"]
