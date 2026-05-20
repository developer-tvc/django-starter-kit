from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from apps.generics.permissions import HasPermission, IsAuthenticated
from apps.generics.responses import api_response
from apps.users import constants
from apps.users.api import schemas
from apps.users.selectors.user_selectors import get_user
from apps.users.serializers import user_serializer
from apps.users.services.user_service import UserService


class UserListCreateView(APIView):
    permission_classes = [HasPermission, IsAuthenticated]
    pagination_class = LimitOffsetPagination
    # Define permissions for each method
    method_permissions = {
        "GET": constants.USER_VIEW,
        "POST": constants.USER_CREATE,
    }

    def get_permissions(self):
        # Dynamically set the required_permission attribute based on HTTP method
        self.required_permission = self.method_permissions.get(self.request.method)
        return super().get_permissions()

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.user_list_schema
    def get(self, request):
        users = UserService.list_users()
        sorted_users = users.order_by("-date_joined")
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(sorted_users, request)
        serializer = user_serializer.UserListSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.user_create_schema
    def post(self, request):
        serializer = user_serializer.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create_user(
            username=serializer.validated_data["username"],
            password=request.data.get("password"),
            first_name=request.data.get("first_name"),
            last_name=request.data.get("last_name"),
            request=request,
        )
        return api_response(
            message="User created successfully.",
            data=user_serializer.UserListSerializer(user).data,
            status_code=status.HTTP_201_CREATED,
        )


class UserRetrieveUpdateDeleteView(APIView):
    permission_classes = [HasPermission, IsAuthenticated]
    # Define permissions for each method
    method_permissions = {
        "GET": constants.USER_VIEW,
        "PUT": constants.USER_UPDATE,
        "DELETE": constants.USER_DELETE,
    }

    def get_permissions(self):
        # Dynamically set the required_permission attribute based on HTTP method
        self.required_permission = self.method_permissions.get(self.request.method)
        return super().get_permissions()

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.user_retrieve_schema
    def get(self, request, user_id):
        user = get_user(user_id)
        if not user:
            return api_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = user_serializer.UserListSerializer(user)
        return api_response(
            message="User retrieved successfully.", data=serializer.data
        )

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.user_update_schema
    def put(self, request, user_id):
        serializer = user_serializer.UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(user_id, serializer.validated_data)
        if not user:
            return api_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = user_serializer.UserListSerializer(user)
        return api_response(message="User updated successfully.", data=serializer.data)

    @method_decorator(
        ratelimit(key="ip", rate="5/m", block=True)  # 5 requests per minute per IP
    )
    @schemas.user_delete_schema
    def delete(self, request, user_id):
        user = UserService.delete_user(user_id)
        if not user:
            return api_response(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return api_response(
            message="User deleted successfully.", status_code=status.HTTP_200_OK
        )
