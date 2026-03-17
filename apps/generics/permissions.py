from rest_framework.permissions import BasePermission, IsAuthenticated


class IsNonAdminUser(BasePermission):
    """
    Allows access only to non admin users.
    """

    def has_permission(self, request, view):
        if not is_authenticated(self, request, view):
            return False

        return bool(request.user and not request.user.is_staff)


class IsSuperUser(BasePermission):
    """
    Allow access only to superusers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
