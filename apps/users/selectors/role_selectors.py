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


def get_role_by_name(name: str):
    """
    Get a role by name
    """
    return Role.objects.filter(name__iexact=name).first()


def get_roles_by_names(names: list):
    """
    Get roles by names
    """
    return Role.objects.filter(name__in=names)