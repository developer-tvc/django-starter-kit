import threading
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import jwt
import pytest
from django.core.exceptions import ObjectDoesNotExist

from apps.generics.responses import api_response
from apps.generics.utils.token_utils import (
    create_password_reset_token,
    decode_password_reset_token,
)
from apps.notifications.models import Notification, NotificationLog
from apps.notifications.services.in_app_service import InAppService
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.services.sms_service import SMSService
from apps.notifications.services.webhook_service import WebhookService
from apps.users.models import UserRole
from apps.users.selectors.auth_selectors import get_client_ip
from apps.users.selectors.role_selectors import (
    get_permission,
    get_role,
    get_role_by_name,
    get_roles_by_names,
    list_permissions,
    list_roles,
)
from apps.users.selectors.user_selectors import (
    get_user,
    get_user_by_username,
    list_users,
)
from apps.users.services.profile_service import ProfileService
from apps.users.services.role_service import RoleService
from apps.users.services.user_service import UserService
from apps.users.tests.factories.user_factory import UserFactory


@pytest.fixture(autouse=True)
def clear_thread_locals():
    thread = threading.current_thread()
    previous_user = getattr(thread, "_django_user", None)
    had_user = hasattr(thread, "_django_user")
    thread._django_user = None
    yield
    if had_user:
        thread._django_user = previous_user
    elif hasattr(thread, "_django_user"):
        delattr(thread, "_django_user")


@pytest.mark.django_db
def test_api_response_and_token_utils(settings):
    response = api_response(data={"id": 1}, message="ok", status_code=201)
    assert response.status_code == 201
    assert response.data == {"success": True, "message": "ok", "data": {"id": 1}}

    token = create_password_reset_token(123)
    assert decode_password_reset_token(token) == 123

    invalid_type = jwt.encode(
        {
            "user_id": 123,
            "exp": datetime.now(UTC) + timedelta(minutes=15),
            "type": "unexpected",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    with pytest.raises(ValueError, match="Invalid token type"):
        decode_password_reset_token(invalid_type)

    expired = jwt.encode(
        {
            "user_id": 123,
            "exp": datetime.now(UTC) - timedelta(minutes=1),
            "type": "password_reset",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    with pytest.raises(ValueError, match="Token expired"):
        decode_password_reset_token(expired)

    with pytest.raises(ValueError, match="Invalid token"):
        decode_password_reset_token("not-a-token")


@pytest.mark.django_db
def test_user_selectors_profile_service_and_user_service():
    actor = UserFactory(first_name="Admin", last_name="User")

    with patch(
        "apps.users.services.user_service.send_notification_task.delay"
    ) as delay:
        created_user = UserService.create_user(
            username="newuser@example.com",
            password="StrongPass123!",
            first_name="New",
            last_name="User",
            request=SimpleNamespace(user=actor),
        )

    created_user.refresh_from_db()
    assert created_user.check_password("StrongPass123!")
    delay.assert_called_once()

    assert get_user(created_user.id) == created_user
    assert get_user_by_username(created_user.username) == created_user
    assert created_user in list(list_users())

    updated_user = UserService.update_user(
        created_user.id,
        {"first_name": "Updated", "avatar_url": "https://img.test/a"},
    )
    assert updated_user.first_name == "Updated"
    assert updated_user.avatar_url == "https://img.test/a"
    assert UserService.update_user(999999, {"first_name": "Missing"}) is None

    profile = ProfileService.get_profile(created_user)
    assert profile == created_user
    ProfileService.update_profile(
        created_user,
        {
            "first_name": "Profiled",
            "last_name": "Person",
            "phone_number": "1234567890",
        },
    )
    created_user.refresh_from_db()
    assert created_user.first_name == "Profiled"
    assert created_user.phone_number == "1234567890"

    deleted_user = UserService.delete_user(created_user.id)
    assert deleted_user.is_active is False
    assert UserService.delete_user(999999) is None


@pytest.mark.django_db
def test_role_selectors_and_role_service_crud():
    permission = RoleService.create_permission("users.view")
    assert get_permission(permission.id) == permission
    assert permission in list(list_permissions())

    with pytest.raises(ValueError, match="already exists"):
        RoleService.create_permission("users.view")

    permission = RoleService.update_permission(permission.id, "users.edit")
    assert permission.name == "users.edit"

    with pytest.raises(ObjectDoesNotExist, match="Permission not found"):
        RoleService.update_permission(999999, "missing")

    role = RoleService.create_role("Manager")
    assert get_role(role.id) == role
    assert get_role_by_name("manager") == role
    assert role in list(list_roles())
    assert list(get_roles_by_names(["Manager"])) == [role]

    with pytest.raises(ValueError, match="already exists"):
        RoleService.create_role("Manager")

    role = RoleService.update_role(role.id, "Team Lead")
    assert role.name == "Team Lead"

    with pytest.raises(ObjectDoesNotExist, match="Role not found"):
        RoleService.update_role(999999, "Missing")

    assigned_role = RoleService.assign_permissions(role.id, [permission.id])
    assert assigned_role.permissions.filter(id=permission.id).exists()

    unassigned_role = RoleService.unassign_permissions(role.id, [permission.id])
    assert not unassigned_role.permissions.filter(id=permission.id).exists()

    user = UserFactory()
    returned_user = RoleService.assign_roles_to_user(user.id, [role.id])
    assert returned_user == user
    assert UserRole.objects.filter(user=user, role=role).exists()

    with pytest.raises(ValueError, match="User Role already exists"):
        RoleService.assign_roles_to_user(user.id, [role.id])

    with pytest.raises(ValueError, match="Roles not found"):
        RoleService.assign_roles_to_user(user.id, [999999])

    unassigned_user = RoleService.unassign_roles_from_user(user.id, [role.id])
    assert unassigned_user == user
    assert not UserRole.objects.filter(user=user, role=role).exists()

    with pytest.raises(ValueError, match="Roles not found"):
        RoleService.unassign_roles_from_user(user.id, [999999])

    RoleService.delete_role(role.id)
    assert get_role(role.id) is None
    with pytest.raises(ObjectDoesNotExist, match="Role not found"):
        RoleService.delete_role(role.id)

    RoleService.delete_permission(permission.id)
    assert get_permission(permission.id) is None
    with pytest.raises(ObjectDoesNotExist, match="Permission not found"):
        RoleService.delete_permission(permission.id)


@pytest.mark.django_db
def test_notification_services_and_client_ip(monkeypatch):
    user = UserFactory()

    InAppService().send(user, "Welcome", "Hello there")
    assert Notification.objects.filter(user=user, title="Welcome").exists()

    webhook_post = Mock()
    monkeypatch.setattr(
        "apps.notifications.services.webhook_service.requests.post", webhook_post
    )
    WebhookService().send(user, "Ping")
    webhook_post.assert_called_once_with(
        "https://example.com/webhook",
        json={"user_id": user.id, "message": "Ping"},
        timeout=5,
    )

    assert SMSService().send(user, "ignored") is None

    monkeypatch.setattr(
        "apps.notifications.services.notification_service.IN_APP_ENABLED", True
    )
    service = NotificationService()
    service.in_app_service.send = Mock()
    logs = service.send([user], "Title", "Body", ["in_app"])
    assert len(logs) == 1
    assert logs[0].status == "sent"
    assert logs[0].sent_at is not None
    service.in_app_service.send.assert_called_once_with(user, "Title", "Body")

    failing_service = NotificationService()
    failing_service.in_app_service.send = Mock(side_effect=RuntimeError("boom"))
    failed_logs = failing_service.send([user], "Fail", "Body", ["in_app"])
    assert len(failed_logs) == 1
    assert failed_logs[0].status == "failed"
    assert failed_logs[0].retry_count == 1
    assert failed_logs[0].payload == {"error": "boom"}
    assert NotificationLog.objects.filter(user=user).count() >= 2

    forwarded_request = SimpleNamespace(
        META={
            "HTTP_X_FORWARDED_FOR": "10.0.0.1, 10.0.0.2",
            "REMOTE_ADDR": "127.0.0.1",
        }
    )
    assert get_client_ip(forwarded_request) == "10.0.0.1"

    direct_request = SimpleNamespace(META={"REMOTE_ADDR": "127.0.0.1"})
    assert get_client_ip(direct_request) == "127.0.0.1"
