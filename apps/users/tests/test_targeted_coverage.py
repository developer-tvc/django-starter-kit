import json
import threading
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.exceptions import TokenError

from apps.activity.models import ActivityLog
from apps.activity.utils import get_diff, serialize_instance
from apps.generics.middleware.exception_handler import GlobalExceptionMiddleware
from apps.notifications.tasks.notification_tasks import send_notification_task
from apps.users import constants
from apps.users.models import Role, UserPermission, UserRole
from apps.users.tests.factories.user_factory import UserFactory
from config import utils


@pytest.fixture(autouse=True)
def clear_django_user_threadlocal():
    thread = threading.current_thread()
    previous_user = getattr(thread, "_django_user", None)
    had_user = hasattr(thread, "_django_user")
    thread._django_user = None
    yield
    if had_user:
        thread._django_user = previous_user
    elif hasattr(thread, "_django_user"):
        delattr(thread, "_django_user")


def grant_permission(user, permission_name):
    permission, _ = UserPermission.objects.get_or_create(name=permission_name)
    role, _ = Role.objects.get_or_create(name=f"role-{permission_name}")
    role.permissions.add(permission)
    UserRole.objects.get_or_create(user=user, role=role)


@pytest.mark.django_db
def test_auth_views_cover_success_and_error_paths():
    client = APIClient()

    with patch("apps.users.api.auth_views.AuthService.login") as login:
        login.return_value = {"access": "a", "refresh": "r", "token_type": "Bearer"}
        response = client.post(
            reverse("login"),
            {"username": "user@example.com", "password": "StrongPass123!"},
            format="json",
        )
    assert response.status_code == 200
    assert response.data["access"] == "a"

    with patch("apps.users.api.auth_views.AuthService.request_password_reset") as reset:
        response = client.post(
            reverse("password_reset_request"),
            {"email": "user@example.com"},
            format="json",
        )
    assert response.status_code == 200
    assert "reset link has been sent" in response.data["message"]
    reset.assert_called_once_with("user@example.com")

    with patch(
        "apps.users.api.auth_views.AuthService.reset_password"
    ) as reset_password:
        response = client.post(
            reverse("password_reset_confirm"),
            {"token": "token-1", "new_password": "StrongPass123!"},
            format="json",
        )
    assert response.status_code == 200
    assert response.data["message"] == "Password reset successful"
    reset_password.assert_called_once_with("token-1", "StrongPass123!")

    with patch(
        "apps.users.api.auth_views.AuthService.reset_password",
        side_effect=ValueError("bad token"),
    ):
        response = client.post(
            reverse("password_reset_confirm"),
            {"token": "token-1", "new_password": "StrongPass123!"},
            format="json",
        )
    assert response.status_code == 400
    assert response.data["detail"] == "bad token"

    response = client.post(reverse("logout"), {}, format="json")
    assert response.status_code == 400
    assert response.data["detail"] == "Refresh token is required"

    mock_token = Mock()
    with (
        patch("apps.users.api.auth_views.RefreshToken", return_value=mock_token),
        patch(
            "apps.users.api.auth_views.BlacklistedToken.objects.filter"
        ) as filter_mock,
    ):
        filter_mock.return_value.exists.return_value = False
        response = client.post(reverse("logout"), {"refresh": "r1"}, format="json")
    assert response.status_code == 200
    assert response.data["detail"] == "Logged out successfully"
    mock_token.blacklist.assert_called_once()

    with (
        patch("apps.users.api.auth_views.RefreshToken", return_value=mock_token),
        patch(
            "apps.users.api.auth_views.BlacklistedToken.objects.filter"
        ) as filter_mock,
    ):
        filter_mock.return_value.exists.return_value = True
        response = client.post(reverse("logout"), {"refresh": "r1"}, format="json")
    assert response.status_code == 401
    assert response.data["detail"] == "Token already blacklisted"

    with patch(
        "apps.users.api.auth_views.RefreshToken",
        side_effect=TokenError("expired"),
    ):
        response = client.post(reverse("logout"), {"refresh": "r1"}, format="json")
    assert response.status_code == 401
    assert "Invalid or expired token: expired" == response.data["detail"]

    with patch("apps.users.api.auth_views.AuthService.verify_email") as verify_email:
        response = client.post(
            reverse("verify-email"), {"token": "verify-token"}, format="json"
        )
    assert response.status_code == 200
    assert response.data["message"] == "Email verification successful"
    verify_email.assert_called_once_with("verify-token")

    with patch(
        "apps.users.api.auth_views.AuthService.verify_email",
        side_effect=ValueError("invalid"),
    ):
        response = client.post(
            reverse("verify-email"), {"token": "verify-token"}, format="json"
        )
    assert response.status_code == 400
    assert response.data["detail"] == "invalid"


@pytest.mark.django_db
def test_role_views_cover_all_methods():
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)

    for permission_name in [
        constants.ROLE_VIEW,
        constants.ROLE_CREATE,
        constants.ROLE_UPDATE,
        constants.ROLE_DELETE,
        constants.PERMISSION_VIEW,
        constants.PERMISSION_CREATE,
        constants.PERMISSION_UPDATE,
        constants.PERMISSION_DELETE,
        constants.ASSIGN_PERMISSION,
        constants.ASSIGN_ROLE,
        constants.UNASSIGN_PERMISSION,
        constants.UNASSIGN_ROLE,
    ]:
        grant_permission(user, permission_name)

    role = Role.objects.create(name="Member")
    permission = UserPermission.objects.create(name="perm:view")
    target_user = UserFactory()

    response = client.get(reverse("role_list_create"))
    assert response.status_code == 200
    assert response.data["message"] == "Roles retrieved successfully."

    response = client.post(
        reverse("role_list_create"), {"name": "Admin"}, format="json"
    )
    assert response.status_code == 201
    assert response.data["data"]["name"] == "Admin"

    with patch(
        "apps.users.api.role_views.RoleService.create_role",
        side_effect=ValueError("duplicate role"),
    ):
        response = client.post(
            reverse("role_list_create"), {"name": "Admin"}, format="json"
        )
    assert response.status_code == 409
    assert response.data["message"] == "duplicate role"

    response = client.put(
        reverse("role_update_destroy", args=[role.id]),
        {"name": "Lead"},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["data"]["name"] == "Lead"

    with patch(
        "apps.users.api.role_views.RoleService.update_role",
        side_effect=ValueError("bad role"),
    ):
        response = client.put(
            reverse("role_update_destroy", args=[role.id]),
            {"name": "Lead"},
            format="json",
        )
    assert response.status_code == 409

    with patch(
        "apps.users.api.role_views.RoleService.update_role",
        side_effect=ObjectDoesNotExist("missing role"),
    ):
        response = client.put(
            reverse("role_update_destroy", args=[role.id]),
            {"name": "Lead"},
            format="json",
        )
    assert response.status_code == 404

    response = client.delete(reverse("role_update_destroy", args=[role.id]))
    assert response.status_code == 200

    with patch(
        "apps.users.api.role_views.RoleService.delete_role",
        side_effect=ValueError("delete failed"),
    ):
        response = client.delete(reverse("role_update_destroy", args=[999]))
    assert response.status_code == 409

    with patch(
        "apps.users.api.role_views.RoleService.delete_role",
        side_effect=ObjectDoesNotExist("missing role"),
    ):
        response = client.delete(reverse("role_update_destroy", args=[999]))
    assert response.status_code == 404

    response = client.get(reverse("permission_list_create"))
    assert response.status_code == 200

    response = client.post(
        reverse("permission_list_create"), {"name": "perm:create"}, format="json"
    )
    assert response.status_code == 201

    with patch(
        "apps.users.api.role_views.RoleService.create_permission",
        side_effect=ValueError("duplicate permission"),
    ):
        response = client.post(
            reverse("permission_list_create"), {"name": "perm:create"}, format="json"
        )
    assert response.status_code == 409

    response = client.put(
        reverse("permission_update_destroy", args=[permission.id]),
        {"name": "perm:updated"},
        format="json",
    )
    assert response.status_code == 200

    with patch(
        "apps.users.api.role_views.RoleService.update_permission",
        side_effect=ValueError("bad permission"),
    ):
        response = client.put(
            reverse("permission_update_destroy", args=[permission.id]),
            {"name": "perm:updated"},
            format="json",
        )
    assert response.status_code == 409

    with patch(
        "apps.users.api.role_views.RoleService.update_permission",
        side_effect=ObjectDoesNotExist("missing permission"),
    ):
        response = client.put(
            reverse("permission_update_destroy", args=[permission.id]),
            {"name": "perm:updated"},
            format="json",
        )
    assert response.status_code == 404

    response = client.delete(reverse("permission_update_destroy", args=[permission.id]))
    assert response.status_code == 200

    with patch(
        "apps.users.api.role_views.RoleService.delete_permission",
        side_effect=ValueError("delete permission failed"),
    ):
        response = client.delete(reverse("permission_update_destroy", args=[999]))
    assert response.status_code == 409

    with patch(
        "apps.users.api.role_views.RoleService.delete_permission",
        side_effect=ObjectDoesNotExist("missing permission"),
    ):
        response = client.delete(reverse("permission_update_destroy", args=[999]))
    assert response.status_code == 404

    role = Role.objects.create(name="Assigned Role")
    permission = UserPermission.objects.create(name="assignable")

    response = client.post(
        reverse("role_permission_assign"),
        {"role_id": role.id, "permission_ids": [permission.id]},
        format="json",
    )
    assert response.status_code == 201

    with patch(
        "apps.users.api.role_views.RoleService.assign_permissions",
        side_effect=ValueError("assign failed"),
    ):
        response = client.post(
            reverse("role_permission_assign"),
            {"role_id": role.id, "permission_ids": [permission.id]},
            format="json",
        )
    assert response.status_code == 409

    response = client.post(
        reverse("user_role_assign"),
        {"user_id": target_user.id, "role_ids": [role.id]},
        format="json",
    )
    assert response.status_code == 201

    with patch(
        "apps.users.api.role_views.RoleService.assign_roles_to_user",
        side_effect=ValueError("assign role failed"),
    ):
        response = client.post(
            reverse("user_role_assign"),
            {"user_id": target_user.id, "role_ids": [role.id]},
            format="json",
        )
    assert response.status_code == 409

    with patch(
        "apps.users.api.role_views.RoleService.assign_roles_to_user",
        side_effect=ObjectDoesNotExist("missing user"),
    ):
        response = client.post(
            reverse("user_role_assign"),
            {"user_id": target_user.id, "role_ids": [role.id]},
            format="json",
        )
    assert response.status_code == 404

    response = client.post(
        reverse("permission_unassign"),
        {"role_id": role.id, "permission_ids": [permission.id]},
        format="json",
    )
    assert response.status_code == 201

    with patch(
        "apps.users.api.role_views.RoleService.unassign_permissions",
        side_effect=ValueError("unassign permission failed"),
    ):
        response = client.post(
            reverse("permission_unassign"),
            {"role_id": role.id, "permission_ids": [permission.id]},
            format="json",
        )
    assert response.status_code == 409

    response = client.post(
        reverse("role_unassign"),
        {"user_id": target_user.id, "role_ids": [role.id]},
        format="json",
    )
    assert response.status_code == 201

    with patch(
        "apps.users.api.role_views.RoleService.unassign_roles_from_user",
        side_effect=ValueError("unassign role failed"),
    ):
        response = client.post(
            reverse("role_unassign"),
            {"user_id": target_user.id, "role_ids": [role.id]},
            format="json",
        )
    assert response.status_code == 409
    with patch(
        "apps.users.api.role_views.RoleService.unassign_roles_from_user",
        side_effect=ObjectDoesNotExist("missing user"),
    ):
        response = client.post(
            reverse("role_unassign"),
            {"user_id": target_user.id, "role_ids": [role.id]},
            format="json",
        )
    assert response.status_code == 404


@pytest.mark.django_db
def test_notification_task_retry_paths():
    failed_log = Mock(status="failed", payload={"error": "boom"})
    sent_log = Mock(status="sent")
    service = Mock()
    service.send.return_value = [failed_log, sent_log]

    task = SimpleNamespace(
        request=SimpleNamespace(retries=0),
        max_retries=3,
        retry=Mock(),
        MaxRetriesExceededError=RuntimeError,
    )

    with patch(
        "apps.notifications.tasks.notification_tasks.NotificationService",
        return_value=service,
    ):
        send_notification_task(task, [1], "Title", "Body", ["in_app"])

    task.retry.assert_called_once()

    retry_exception = RuntimeError("max retries")
    task = SimpleNamespace(
        request=SimpleNamespace(retries=0),
        max_retries=3,
        retry=Mock(side_effect=retry_exception),
        MaxRetriesExceededError=RuntimeError,
    )
    log = Mock(status="failed", payload={"error": "boom"})
    service.send.return_value = [log]

    with patch(
        "apps.notifications.tasks.notification_tasks.NotificationService",
        return_value=service,
    ):
        send_notification_task(task, [1], "Title", "Body", ["in_app"])

    assert log.status == "failed"
    assert log.retry_count == 3
    log.save.assert_called_once()

    task = SimpleNamespace(
        request=SimpleNamespace(retries=3),
        max_retries=3,
        retry=Mock(),
        MaxRetriesExceededError=RuntimeError,
    )
    service.send.return_value = [Mock(status="failed", payload={"error": "boom"})]
    with patch(
        "apps.notifications.tasks.notification_tasks.NotificationService",
        return_value=service,
    ):
        send_notification_task(task, [1], "Title", "Body", ["in_app"])
    task.retry.assert_not_called()


def test_config_utils_and_exception_middleware(tmp_path, monkeypatch):
    monkeypatch.setenv("COVERAGE_TEST_ENV", "value-1")
    assert utils.get_env_variable("COVERAGE_TEST_ENV") == "value-1"

    monkeypatch.delenv("MISSING_ENV", raising=False)
    with pytest.raises(ValueError, match="MISSING_ENV Environment variable not set"):
        utils.get_env_variable("MISSING_ENV")

    sample = tmp_path / "sample.txt"
    sample.write_text("ok", encoding="utf-8")
    assert utils.validate_file_path(str(sample)) == str(sample)
    assert utils.validate_file_path(None) is None

    with pytest.raises(RuntimeError, match="does not exist"):
        utils.validate_file_path(str(tmp_path / "missing.txt"))

    request = SimpleNamespace(
        path="/boom",
        method="GET",
        user=SimpleNamespace(is_authenticated=True, id=77),
    )
    logger = Mock()
    monkeypatch.setattr(
        "apps.generics.middleware.exception_handler.logger.error", logger
    )
    middleware = GlobalExceptionMiddleware(lambda req: HttpResponse("ok"))
    response = middleware.process_exception(request, RuntimeError("failure"))
    assert response.status_code == 500
    assert json.loads(response.content) == {"detail": "An unexpected error occurred."}
    logged_data = logger.call_args[0][0]
    assert logged_data["message"] == "failure"
    assert logged_data["user_id"] == 77

    anon_request = SimpleNamespace(
        path="/boom",
        method="POST",
        user=SimpleNamespace(is_authenticated=False),
    )
    logger.reset_mock()
    middleware.process_exception(anon_request, RuntimeError("other"))
    logged_data = logger.call_args[0][0]
    assert "user_id" not in logged_data


@pytest.mark.django_db
def test_activity_utils_and_mixin_behavior():
    actor = UserFactory(first_name="Audit", last_name="User")
    thread = threading.current_thread()

    role = Role.objects.create(name="Serializable")
    serialized = serialize_instance(role)
    assert serialized["name"] == "Serializable"

    original = Role.objects.create(name="Original")
    original.name = "Updated"
    diff = get_diff(Role.objects.get(pk=original.pk), original)
    assert diff == {"old": {"name": "Original"}, "new": {"name": "Updated"}}
    assert (
        get_diff(Role.objects.get(pk=original.pk), Role.objects.get(pk=original.pk))
        is None
    )

    thread._django_user = None
    role = Role.objects.create(name="No Audit")
    assert not ActivityLog.objects.filter(object_id=role.pk).exists()

    thread._django_user = AnonymousUser()
    role = Role.objects.create(name="Anonymous")
    assert not ActivityLog.objects.filter(object_id=role.pk).exists()

    thread._django_user = actor
    role = Role.objects.create(name="Created Role")
    create_log = ActivityLog.objects.filter(object_id=role.pk).latest("id")
    assert create_log.action == "role created"
    assert "created by Audit User" == create_log.description
    assert create_log.new_value["name"] == "Created Role"

    role.name = "Updated Role"
    role.description = "A new description"
    role.save()
    update_log = ActivityLog.objects.filter(
        object_id=role.pk, action="role updated"
    ).latest("id")
    assert "changed name from Created Role" in update_log.description
    assert "added description" in update_log.description
    assert update_log.old_value["name"] == "Created Role"
    assert update_log.new_value["name"] == "Updated Role"

    role.description = None
    role.save()
    remove_log = ActivityLog.objects.filter(
        object_id=role.pk, action="role updated"
    ).latest("id")
    assert "removed description (was A new description)" in remove_log.description

    log_count = ActivityLog.objects.count()
    role.save()
    assert ActivityLog.objects.count() == log_count

    role.delete()
    delete_log = ActivityLog.objects.filter(action="role deleted").latest("id")
    assert "role deleted by Audit User" == delete_log.description
    assert delete_log.old_value["name"] == "Updated Role"
