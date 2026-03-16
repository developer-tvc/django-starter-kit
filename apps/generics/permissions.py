from rest_framework.permissions import BasePermission, IsAuthenticated

from users import configurations, models


def is_authenticated(self, request, view):
    return IsAuthenticated.has_permission(self, request, view)


class IsNonAdminUser(BasePermission):
    """
    Allows access only to non admin users.
    """

    def has_permission(self, request, view):
        if not is_authenticated(self, request, view):
            return False

        return bool(request.user and not request.user.is_staff)


def is_user_permitted(request, role_name):
    pass

    return True

