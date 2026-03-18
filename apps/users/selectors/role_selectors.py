from apps.users.models import Role, UserPermission


def list_roles():
    """
    List all roles
    """
    return Role.objects.all()


def get_role(role_id):
    """
    Get a role by ID
    """
    return Role.objects.filter(id=role_id).first()


def list_permissions():
    """
    List all permissions
    """
    return UserPermission.objects.all()


def get_permission(permission_id):
    """
    Get a permission by ID
    """
    return UserPermission.objects.filter(id=permission_id).first()
