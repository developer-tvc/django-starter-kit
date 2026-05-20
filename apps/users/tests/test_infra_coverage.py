import json
import logging
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from rest_framework_simplejwt.exceptions import InvalidToken

from apps.activity.models import UserDevice
from apps.activity.services.device_track import track_device
from apps.generics.middleware.correlation_id_middleware import (
    CorrelationIdMiddleware,
    get_current_correlation_id,
)
from apps.generics.middleware.current_user_middleware import (
    CurrentUserMiddleware,
    get_current_user,
    get_user,
)
from apps.generics.middleware.device_middleware import DeviceMiddleware
from apps.generics.middleware.ip_whitelist_middleware import IPWhitelistMiddleware
from apps.generics.utils.logging_filters import CorrelationIdFilter
from apps.monitoring.api.views import HealthView, ReadinessView
from apps.users.tests.factories.user_factory import UserFactory


class SuccessfulCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query):
        self.query = query

    def fetchone(self):
        return (1,)


class FailingCursor(SuccessfulCursor):
    def execute(self, query):
        raise RuntimeError("db down")


AUTHENTICATE_PATH = (
    "apps.generics.middleware.current_user_middleware." "JWTAuthentication.authenticate"
)


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
def test_monitoring_views_success_and_failure(monkeypatch):
    factory = RequestFactory()

    monkeypatch.setattr(
        "apps.monitoring.api.views.connection.cursor", lambda: SuccessfulCursor()
    )
    health_response = HealthView.as_view()(factory.get("/health"))
    assert health_response.status_code == 200
    assert json.loads(health_response.content) == {"status": "ok", "database": "ok"}

    class HealthyRedis:
        def ping(self):
            return True

    monkeypatch.setattr(
        "apps.monitoring.api.views.redis.Redis", lambda **kwargs: HealthyRedis()
    )
    readiness_response = ReadinessView.as_view()(factory.get("/ready"))
    assert readiness_response.status_code == 200
    assert json.loads(readiness_response.content) == {
        "status": "ready",
        "details": {"database": "ok", "redis": "ok"},
    }

    monkeypatch.setattr(
        "apps.monitoring.api.views.connection.cursor", lambda: FailingCursor()
    )

    class FailingRedis:
        def ping(self):
            raise RuntimeError("redis down")

    monkeypatch.setattr(
        "apps.monitoring.api.views.redis.Redis", lambda **kwargs: FailingRedis()
    )
    failed_readiness = ReadinessView.as_view()(factory.get("/ready"))
    assert failed_readiness.status_code == 503
    payload = json.loads(failed_readiness.content)
    assert payload["status"] == "not ready"
    assert payload["details"]["database"].startswith("error:")
    assert payload["details"]["redis"].startswith("error:")


def test_device_and_ip_whitelist_middleware(monkeypatch):
    factory = RequestFactory()
    request = factory.get(
        "/device",
        HTTP_X_FORWARDED_FOR="10.0.0.1, 10.0.0.2",
        HTTP_USER_AGENT="pytest-agent",
    )

    monkeypatch.setattr(
        "apps.generics.middleware.device_middleware.uuid.uuid4",
        lambda: "generated-id",
    )
    response = DeviceMiddleware(lambda req: HttpResponse("ok"))(request)
    assert response.status_code == 200
    assert request.device_id == "generated-id"
    assert request.user_agent == "pytest-agent"
    assert request.ip_address == "10.0.0.1"

    with override_settings(IP_WHITELIST=["127.0.0.1"]):
        allow_request = factory.get("/secure", REMOTE_ADDR="127.0.0.1")
        allowed = IPWhitelistMiddleware(lambda req: HttpResponse("ok"))(allow_request)
        assert allowed.status_code == 200

        deny_request = factory.get("/secure", REMOTE_ADDR="10.10.10.10")
        denied = IPWhitelistMiddleware(lambda req: HttpResponse("ok"))(deny_request)
        assert denied.status_code == 403
        assert json.loads(denied.content) == {"detail": "Access denied: IP not allowed"}


@pytest.mark.django_db
def test_current_user_middleware_helpers_and_tracking(monkeypatch):
    factory = RequestFactory()
    request = factory.get("/me")
    request.user = UserFactory()

    monkeypatch.setattr(AUTHENTICATE_PATH, lambda self, req: (request.user, None))
    assert get_user(request) == request.user

    monkeypatch.setattr(AUTHENTICATE_PATH, lambda self, req: None)
    assert get_user(request) is None

    monkeypatch.setattr(AUTHENTICATE_PATH, lambda self, req: (AnonymousUser(), None))
    assert get_user(request) is None

    def raise_invalid(self, req):
        raise InvalidToken("bad token")

    monkeypatch.setattr(AUTHENTICATE_PATH, raise_invalid)
    invalid_response = get_user(request)
    assert invalid_response.status_code == 401

    monkeypatch.setattr(
        "apps.generics.middleware.current_user_middleware.get_user",
        lambda req: request.user,
    )
    middleware = CurrentUserMiddleware(lambda req: HttpResponse("ok"))
    response = middleware(request)
    assert response.status_code == 200
    assert get_current_user() == request.user

    no_device_request = SimpleNamespace(
        device_id=None, user_agent="ua", ip_address="1.1.1.1"
    )
    track_device(no_device_request, request.user)
    assert UserDevice.objects.count() == 0

    tracked_request = SimpleNamespace(
        device_id="device-1",
        user_agent="agent-1",
        ip_address="1.1.1.1",
    )
    track_device(tracked_request, request.user)
    device = UserDevice.objects.get(user=request.user, device_id="device-1")
    assert device.user_agent == "agent-1"

    tracked_request.user_agent = "agent-2"
    tracked_request.ip_address = "2.2.2.2"
    track_device(tracked_request, request.user)
    device.refresh_from_db()
    assert device.user_agent == "agent-2"
    assert device.ip_address == "2.2.2.2"
    assert str(device).startswith(f"{request.user.id} - ")


def test_correlation_middleware_and_logging_filter(monkeypatch):
    factory = RequestFactory()
    request = factory.get("/correlated")
    request.user = SimpleNamespace(id=42, is_authenticated=True)

    info_logger = Mock()
    monkeypatch.setattr(
        "apps.generics.middleware.correlation_id_middleware.logger.info", info_logger
    )

    response = CorrelationIdMiddleware(lambda req: HttpResponse("ok"))(request)
    assert response.status_code == 200
    assert response["X-Correlation-ID"]
    assert get_current_correlation_id() == request.correlation_id
    assert info_logger.call_count == 2

    exception_logger = Mock()
    monkeypatch.setattr(
        "apps.generics.middleware.correlation_id_middleware.logger.exception",
        exception_logger,
    )

    failing_request = factory.get("/correlated-fail")
    failing_request.user = SimpleNamespace(id=7, is_authenticated=True)
    middleware = CorrelationIdMiddleware(
        lambda req: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    with pytest.raises(RuntimeError, match="boom"):
        middleware(failing_request)
    exception_logger.assert_called_once()

    monkeypatch.setattr(
        "apps.generics.middleware.current_user_middleware.get_current_user",
        lambda: SimpleNamespace(user=99),
    )
    monkeypatch.setattr(
        "apps.generics.middleware.correlation_id_middleware.get_current_correlation_id",
        lambda: "corr-id",
    )
    record = logging.LogRecord("apps", logging.INFO, __file__, 1, "message", (), None)
    assert CorrelationIdFilter().filter(record) is True
    assert record.user_id == 99
    assert record.correlation_id == "corr-id"
