from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.views import APIView

from apps.generics.permissions import HasPermission, IsAuthenticated
from apps.generics.responses import api_response
from apps.users import constants
from apps.users.api import schemas
from apps.users.selectors.role_selectors import list_permissions, list_roles
from apps.users.serializers import role_serializer
from apps.users.services.role_service import RoleService


class RoleListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    # Define permissions for each method
    method_permissions = {
        "GET": constants.ROLE_VIEW,
        "POST": constants.ROLE_CREATE,
    }

    def get_permissions(self):
        # Dynamically set the required_permission attribute based on HTTP method
        self.required_permission = self.method_permissions.get(self.request.method)
        return super().get_permissions()

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.role_list_schema
    def get(self, request):
        roles = list_roles()
        serializer = role_serializer.RoleListSerializer(roles, many=True)
        return api_response(
            message="Roles retrieved successfully.", data=serializer.data
        )

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.role_create_schema
    def post(self, request):
        serializer = role_serializer.RoleSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.create_role(serializer.validated_data["name"])
            serializer = role_serializer.RoleSerializer(role)
            return api_response(
                message="Role created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class RoleUpdateDestroyView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    # Define permissions for each method
    method_permissions = {
        "GET": constants.ROLE_UPDATE,
        "POST": constants.ROLE_DELETE,
    }

    def get_permissions(self):
        # Dynamically set the required_permission attribute based on HTTP method
        self.required_permission = self.method_permissions.get(self.request.method)
        return super().get_permissions()

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.role_update_schema
    def put(self, request, role_id):
        serializer = role_serializer.RoleSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.update_role(role_id, serializer.validated_data["name"])
            serializer = role_serializer.RoleSerializer(role)
            return api_response(
                message="Role updated successfully.", data=serializer.data
            )
        except ObjectDoesNotExist as e:
            return api_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.role_delete_schema
    def delete(self, request, role_id):
        try:
            RoleService.delete_role(role_id)
            return api_response(message="Role deleted successfully.")
        except ObjectDoesNotExist as e:
            return api_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class PermissionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    # Define permissions for each method
    method_permissions = {
        "GET": constants.PERMISSION_VIEW,
        "POST": constants.PERMISSION_CREATE,
    }

    def get_permissions(self):
        # Dynamically set the required_permission attribute based on HTTP method
        self.required_permission = self.method_permissions.get(self.request.method)
        return super().get_permissions()

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.permission_list_schema
    def get(self, request):
        permissions = list_permissions()
        serializer = role_serializer.PermissionSerializer(permissions, many=True)
        return api_response(
            message="Permissions retrieved successfully.", data=serializer.data
        )

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.permission_create_schema
    def post(self, request):
        serializer = role_serializer.PermissionSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            permission = RoleService.create_permission(
                serializer.validated_data["name"]
            )
            serializer = role_serializer.PermissionSerializer(permission)
            return api_response(
                message="Permission created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class PermissionUpdateDestroyView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    # Define permissions for each method
    method_permissions = {
        "GET": constants.PERMISSION_UPDATE,
        "POST": constants.PERMISSION_DELETE,
    }

    def get_permissions(self):
        # Dynamically set the required_permission attribute based on HTTP method
        self.required_permission = self.method_permissions.get(self.request.method)
        return super().get_permissions()

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.permission_update_schema
    def put(self, request, permission_id):
        serializer = role_serializer.PermissionSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            permission = RoleService.update_permission(
                permission_id, serializer.validated_data["name"]
            )
            serializer = role_serializer.PermissionSerializer(permission)
            return api_response(
                message="Permission updated successfully.", data=serializer.data
            )
        except ObjectDoesNotExist as e:
            return api_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.permission_delete_schema
    def delete(self, request, permission_id):
        try:
            RoleService.delete_permission(permission_id)
            return api_response(message="Permission deleted successfully.")
        except ObjectDoesNotExist as e:
            return api_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class RolePermissionAssignView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = constants.ASSIGN_PERMISSION

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.role_permission_assign_schema
    def post(self, request):
        serializer = role_serializer.RolePermissionAssignSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.assign_permissions(
                serializer.validated_data["role_id"],
                serializer.validated_data["permission_ids"],
            )
            serializer = role_serializer.RoleSerializer(role)
            return api_response(
                message="Permissions assigned to role successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class UserRoleAssignView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = constants.ASSIGN_ROLE

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.user_role_assign_schema
    def post(self, request):
        serializer = role_serializer.UserRoleAssignSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            RoleService.assign_roles_to_user(
                serializer.validated_data["user_id"],
                serializer.validated_data["role_ids"],
            )
            return api_response(
                message="Roles assigned to user successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        except ObjectDoesNotExist as e:
            return api_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class PermissionUnassignView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = constants.UNASSIGN_PERMISSION

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.permission_unassign_schema
    def post(self, request):
        serializer = role_serializer.RolePermissionAssignSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.unassign_permissions(
                serializer.validated_data["role_id"],
                serializer.validated_data["permission_ids"],
            )
            serializer = role_serializer.RoleSerializer(role)
            return api_response(
                message="Permissions unassigned from role successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class RoleUnassignView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = constants.UNASSIGN_ROLE

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.role_unassign_schema
    def post(self, request):
        serializer = role_serializer.UserRoleAssignSerializer(
            data=request.data
        )  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            RoleService.unassign_roles_from_user(
                serializer.validated_data["user_id"],
                serializer.validated_data["role_ids"],
            )
            return api_response(
                message="Roles unassigned from user successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        except ObjectDoesNotExist as e:
            return api_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)
