from drf_spectacular.utils import extend_schema
from apps.users.serializers.auth_serializer import LoginSerializer
from apps.users.serializers import role_serializer

login_schema = extend_schema(
    tags=["Auth"],
    summary="User Login",
    description="Authenticate user and return access and refresh tokens.",
    request=LoginSerializer,
    responses={
        200: dict,
        401: dict,
    },
)


role_create_schema = extend_schema(
    tags=["Roles"],
    summary="Create Role",
    description="Create a new role in the system.",
    request=role_serializer.RoleSerializer,
    responses={
        201: role_serializer.RoleSerializer,
        400: dict,
    },
)


role_list_schema = extend_schema(
    tags=["Roles"],
    summary="List Roles",
    description="Returns all roles available in the system.",
    responses={
        200: role_serializer.RoleSerializer(many=True),
    },
)

permission_list_schema = extend_schema(
    tags=["Permissions"],
    summary="List permissions",
    description="Returns all system permissions.",
    responses={
        200: role_serializer.PermissionSerializer(many=True),
    },
)

permission_create_schema = extend_schema(
    tags=["Permissions"],
    summary="Create Permission",
    description="Create a new permission in the system.",
    request=role_serializer.PermissionSerializer,
    responses={
        201: role_serializer.PermissionSerializer,
        400: dict,
    },
)

permission_update_schema = extend_schema(
    tags=["Permissions"],
    summary="Update Permission",
    description="Update a permission in the system.",
    request=role_serializer.PermissionSerializer,
    responses={
        200: role_serializer.PermissionSerializer,
        400: dict,
    },
)

permission_delete_schema = extend_schema(
    tags=["Permissions"],
    summary="Delete Permission",
    description="Delete a permission from the system.",
    responses={
        200: dict,
        400: dict,
    },
)

role_permission_assign_schema = extend_schema(
    tags=["Roles"],
    summary="Assign Permissions to Role",
    description="Assign permissions to a role.",
    request=role_serializer.RolePermissionAssignSerializer,
    responses={
        201: role_serializer.RoleSerializer,
        400: dict,
    },
)

role_update_schema = extend_schema(
    tags=["Roles"],
    summary="Update Role",
    description="Update a role in the system.",
    request=role_serializer.RoleSerializer,
    responses={
        200: role_serializer.RoleSerializer,
        400: dict,
    },
)

role_delete_schema = extend_schema(
    tags=["Roles"],
    summary="Delete Role",
    description="Delete a role from the system.",
    responses={
        200: dict,
        400: dict,
    },
)

user_role_assign_schema = extend_schema(
    tags=["Roles"],
    summary="Assign Roles to User",
    description="Assign roles to a user.",
    request=role_serializer.UserRoleAssignSerializer,
    responses={
        201: dict,
        400: dict,
    },
)
