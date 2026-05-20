from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from apps.users.models import Role, UserPermission, UserRole

User = get_user_model()


class RoleService:

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def create_permission(permission_name: str) -> UserPermission:
        """
        Create a new permission in the system.
        """
        if UserPermission.objects.filter(name=permission_name).exists():
            raise ValueError(f"Permission '{permission_name}' already exists")

        permission = UserPermission.objects.create(name=permission_name)
        return permission

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def update_permission(permission_id: int, permission_name: str) -> UserPermission:
        """
        Update a permission in the system.
        """
        try:
            permission = UserPermission.objects.get(id=permission_id)
        except UserPermission.DoesNotExist:
            raise ObjectDoesNotExist("Permission not found")

        permission.name = permission_name
        permission.save()

        return permission

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def delete_permission(permission_id: int) -> None:
        """
        Delete a permission from the system.
        """
        try:
            permission = UserPermission.objects.get(id=permission_id)
        except UserPermission.DoesNotExist:
            raise ObjectDoesNotExist("Permission not found")

        permission.delete()

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def create_role(role_name: str) -> Role:
        """
        Create a new role in the system.
        """
        if Role.objects.filter(name=role_name).exists():
            raise ValueError(f"Role '{role_name}' already exists")

        role = Role.objects.create(name=role_name)
        return role

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def update_role(role_id: int, role_name: str) -> Role:
        """
        Update a role in the system.
        """
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise ObjectDoesNotExist("Role not found")

        role.name = role_name
        role.save()

        return role

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def delete_role(role_id: int) -> None:
        """
        Delete a role from the system.
        """
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise ObjectDoesNotExist("Role not found")

        role.delete()

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def assign_permissions(role_id: int, permission_ids: list[int]) -> Role:
        """
        Assign permissions to a role
        """

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise ObjectDoesNotExist("Role not found")

        permissions = UserPermission.objects.filter(id__in=permission_ids)

        role.permissions.add(*permissions)

        return role

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def assign_roles_to_user(user_id: int, role_ids: list[int]) -> User:
        """
        Assign roles to a user
        """

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ObjectDoesNotExist("User not found")

        existing_user_roles = UserRole.objects.filter(user=user, role_id__in=role_ids)
        if existing_user_roles.exists():
            raise ValueError("User Role already exists")

        roles = Role.objects.filter(id__in=role_ids)
        if not roles.exists():
            raise ValueError("Roles not found")

        for role in roles:
            UserRole.objects.create(user=user, role=role)

        return user

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def assign_permissions_to_user(user_id: int, permission_ids: list[int]) -> User:
        """
        Assign permissions to a user
        """

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ObjectDoesNotExist("User not found")

        permissions = UserPermission.objects.filter(id__in=permission_ids)

        user.permissions.set(permissions)

        return user

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def unassign_permissions(role_id: int, permission_ids: list[int]) -> Role:
        """
        Unassign permissions from a role
        """

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise ObjectDoesNotExist("Role not found")

        permissions = UserPermission.objects.filter(id__in=permission_ids)

        role.permissions.remove(*permissions)

        return role

    @staticmethod  # Static service method to avoid unnecessary class instantiation
    @transaction.atomic
    def unassign_roles_from_user(user_id: int, role_ids: list[int]) -> User:
        """
        Unassign roles from a user
        """

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ObjectDoesNotExist("User not found")

        roles = Role.objects.filter(id__in=role_ids)
        if not roles.exists():
            raise ValueError("Roles not found")

        for role in roles:
            UserRole.objects.filter(user=user, role=role).delete()

        return user
