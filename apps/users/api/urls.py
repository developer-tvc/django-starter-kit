from django.urls import path
from apps.users.api import auth_views, role_views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("refresh/", auth_views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", auth_views.CustomTokenBlacklistView.as_view(), name="token_blacklist"),

    path("roles/", role_views.RoleListCreateView.as_view()),
    path("roles/<int:role_id>/", role_views.RoleUpdateDestroyView.as_view()),
    path("permissions/", role_views.PermissionListCreateView.as_view()),
    path("permissions/<int:permission_id>/", role_views.PermissionUpdateDestroyView.as_view()),
    path("permissions/assign/", role_views.RolePermissionAssignView.as_view()),
    path("roles/assign/", role_views.UserRoleAssignView.as_view()),
]   