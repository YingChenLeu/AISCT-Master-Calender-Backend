from rest_framework.permissions import BasePermission

from .models import Authority


def get_authority(user):
    if not user.is_authenticated:
        return Authority.GUEST

    try:
        return user.profile.authority
    except Exception:
        return Authority.GUEST


class CanModifyEvents(BasePermission):
    """
    StuCo, teachers, and admins.
    """

    def has_permission(self, request, view):
        authority = get_authority(request.user)

        return authority >= Authority.STUCO


class CanModifyAssignments(BasePermission):
    """
    Teachers and admins.
    """

    def has_permission(self, request, view):
        authority = get_authority(request.user)

        return authority >= Authority.TEACHER


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        authority = get_authority(request.user)

        return authority == Authority.ADMIN
