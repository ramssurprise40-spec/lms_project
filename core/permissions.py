from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "instructor"
        )


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "student"
        )


class IsCourseInstructor(BasePermission):
    """
    Allows access only to users who are instructors of the course.
    Assumes the object has an 'instructor' field.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == getattr(
            obj, "instructor", None
        )
