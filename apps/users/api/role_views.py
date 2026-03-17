from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.users.services.role_service import RoleService
from apps.users.selectors.role_selectors import list_roles, list_permissions
from apps.users.serializers import role_serializer
from apps.users.api import schemas
from apps.generics.permissions import IsSuperUser
from apps.generics.responses import api_response

class RoleListCreateView(APIView):

    permission_classes = [IsSuperUser]
    @schemas.role_list_schema
    def get(self, request):
        roles = list_roles()
        serializer = role_serializer.RoleListSerializer(roles, many=True)
        return api_response(message="Roles retrieved successfully.", data=serializer.data)

    @schemas.role_create_schema
    def post(self, request):
        serializer = role_serializer.RoleSerializer(data=request.data)  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.create_role(serializer.validated_data["name"])
            serializer = role_serializer.RoleSerializer(role)
            return api_response(message="Role created successfully.", data=serializer.data, status_code=status.HTTP_201_CREATED)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)

class RoleUpdateDestroyView(APIView):
    permission_classes = [IsSuperUser]
    @schemas.role_update_schema
    def put(self, request, role_id):
        serializer = role_serializer.RoleSerializer(data=request.data)  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.update_role(role_id, serializer.validated_data["name"])
            serializer = role_serializer.RoleSerializer(role)
            return api_response(message="Role updated successfully.", data=serializer.data)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)

    @schemas.role_delete_schema
    def delete(self, request, role_id):
        try:
            role = RoleService.delete_role(role_id)
            return api_response(message="Role deleted successfully.")
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class PermissionListCreateView(APIView):
    permission_classes = [IsSuperUser]
    @schemas.permission_list_schema
    def get(self, request):
        permissions = list_permissions()
        serializer = role_serializer.PermissionSerializer(permissions, many=True)
        return api_response(message="Permissions retrieved successfully.", data=serializer.data)

    @schemas.permission_create_schema
    def post(self, request):
        serializer = role_serializer.PermissionSerializer(data=request.data)  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            permission = RoleService.create_permission(serializer.validated_data["name"])
            serializer = role_serializer.PermissionSerializer(permission)
            return api_response(message="Permission created successfully.", data=serializer.data, status_code=status.HTTP_201_CREATED)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)

class PermissionUpdateDestroyView(APIView):
    permission_classes = [IsSuperUser]
    @schemas.permission_update_schema
    def put(self, request, permission_id):
        serializer = role_serializer.PermissionSerializer(data=request.data)  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            permission = RoleService.update_permission(permission_id, serializer.validated_data["name"])
            serializer = role_serializer.PermissionSerializer(permission)
            return api_response(message="Permission updated successfully.", data=serializer.data)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)

    @schemas.permission_delete_schema
    def delete(self, request, permission_id):
        try:
            permission = RoleService.delete_permission(permission_id)
            return api_response(message="Permission deleted successfully.")
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)
        


class RolePermissionAssignView(APIView):
    permission_classes = [IsSuperUser]
    @schemas.role_permission_assign_schema
    def post(self, request):
        serializer = role_serializer.RolePermissionAssignSerializer(data=request.data)  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            role = RoleService.assign_permissions(serializer.validated_data["role_id"], serializer.validated_data["permission_ids"])
            serializer = role_serializer.RoleSerializer(role)
            return api_response(message="Permissions assigned to role successfully.", data=serializer.data, status_code=status.HTTP_201_CREATED)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)


class UserRoleAssignView(APIView):
    permission_classes = [IsSuperUser]
    @schemas.user_role_assign_schema
    def post(self, request):
        serializer = role_serializer.UserRoleAssignSerializer(data=request.data)  # Validate the data
        serializer.is_valid(raise_exception=True)
        try:
            user = RoleService.assign_roles_to_user(serializer.validated_data["user_id"], serializer.validated_data["role_ids"])
            return api_response(message="Roles assigned to user successfully.", status_code=status.HTTP_201_CREATED)
        except ValueError as e:
            return api_response(message=str(e), status_code=status.HTTP_409_CONFLICT)
