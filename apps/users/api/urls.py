from django.urls import path

from apps.users.api import auth_views, profile_views, role_views, user_views

urlpatterns = [
    path("", user_views.UserListCreateView.as_view(), name="user-list-create"),
    path(
        "<int:user_id>/",
        user_views.UserRetrieveUpdateDeleteView.as_view(),
        name="user-detail",
    ),
    path("profile/", profile_views.ProfileView.as_view(), name="profile"),
    path(
        "verify-email/", auth_views.EmailVerificationView.as_view(), name="verify-email"
    ),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("refresh/", auth_views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path(
        "logout/", auth_views.CustomTokenBlacklistView.as_view(), name="token_blacklist"
    ),
    path("roles/", role_views.RoleListCreateView.as_view(), name="role_list_create"),
    path(
        "roles/<int:role_id>/",
        role_views.RoleUpdateDestroyView.as_view(),
        name="role_update_destroy",
    ),
    path(
        "permissions/",
        role_views.PermissionListCreateView.as_view(),
        name="permission_list_create",
    ),
    path(
        "permissions/<int:permission_id>/",
        role_views.PermissionUpdateDestroyView.as_view(),
        name="permission_update_destroy",
    ),
    path(
        "permissions/assign/",
        role_views.RolePermissionAssignView.as_view(),
        name="role_permission_assign",
    ),
    path(
        "roles/assign/",
        role_views.UserRoleAssignView.as_view(),
        name="user_role_assign",
    ),
    path(
        "permissions/unassign/",
        role_views.PermissionUnassignView.as_view(),
        name="permission_unassign",
    ),
    path(
        "roles/unassign/", role_views.RoleUnassignView.as_view(), name="role_unassign"
    ),
    path(
        "password/reset/request/",
        auth_views.PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password/reset/confirm/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
