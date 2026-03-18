from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.users.models import UserRole


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
        return bool(
            request.user and request.user.is_authenticated and request.user.is_superuser
        )


class HasPermission(BasePermission):
    """
    Custom RBAC permission:
    - Checks if the authenticated user has a given permission via their roles.
    - The view must define a 'required_permission' attribute (string).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        required_permission = getattr(view, "required_permission", None)
        if not required_permission:
            return True  # No permission required, allow access

        # Get all roles of the user
        user_roles = UserRole.objects.filter(user=user).prefetch_related(
            "role__permissions"
        )
        # Check if any role has the required permission
        for user_role in user_roles:
            if user_role.role.permissions.filter(name=required_permission).exists():
                return True

        return False


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
