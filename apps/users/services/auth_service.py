from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from apps.activity.services.device_track import track_device
from apps.generics.utils.token_utils import (
    create_password_reset_token,
    decode_password_reset_token,
)
from apps.notifications.services.email_service import EmailService
from apps.users.selectors.auth_selectors import get_client_ip
from apps.users.selectors.user_selectors import get_user_by_username

User = get_user_model()
INVALID_CREDENTIALS_MESSAGE = "Invalid username or password"


class AuthService:
    @staticmethod
    def login(username: str, password: str, request):
        now = timezone.now()
        auth_user = authenticate(username=username, password=password)
        stored_user = get_user_by_username(username)

        if not stored_user:
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

        AuthService._handle_login_lock_state(stored_user, now)

        if not auth_user:
            AuthService._handle_failed_login(stored_user, password)
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

        if not auth_user.is_active:
            raise AuthenticationFailed("Account is disabled")

        if not auth_user.is_email_verified:
            raise AuthenticationFailed("Account is not verified")

        AuthService._reset_failed_login_state(auth_user)
        AuthService._update_login_metadata(auth_user, request, now)

        # Issue JWT tokens
        refresh = RefreshToken.for_user(auth_user)
        track_device(request, auth_user)
        return {
            "token_type": "Bearer",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def _handle_login_lock_state(user, now):
        if AuthService._is_lock_enabled():
            AuthService._raise_if_account_locked(user, now)
            if AuthService._lock_has_expired(user, now):
                AuthService._clear_login_lock(user)
            return

        if user.is_locked and user.locked_until:
            AuthService._clear_login_lock(user)

    @staticmethod
    def _raise_if_account_locked(user, now):
        if not AuthService._is_account_locked(user, now):
            return

        remaining_seconds = int((user.locked_until - now).total_seconds())
        remaining_minutes = remaining_seconds // 60
        remaining_seconds = remaining_seconds % 60
        raise AuthenticationFailed(
            "Account locked. "
            f"Try again in {remaining_minutes}m {remaining_seconds}s"
        )

    @staticmethod
    def _handle_failed_login(user, password):
        if user.check_password(password) or not AuthService._is_lock_enabled():
            return

        user.failed_login_attempts += 1
        if int(user.failed_login_attempts) >= int(settings.LOGIN_MAX_ATTEMPTS):
            user.is_locked = True
            user.locked_until = timezone.now() + timedelta(
                minutes=int(settings.LOGIN_LOCK_MINUTES)
            )

        user.save(
            update_fields=["failed_login_attempts", "is_locked", "locked_until"]
        )

    @staticmethod
    def _reset_failed_login_state(user):
        if not AuthService._is_lock_enabled():
            return

        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "is_locked", "locked_until"])

    @staticmethod
    def _update_login_metadata(user, request, now):
        user.last_login = now
        user.ip_address = get_client_ip(request)
        user.save(update_fields=["last_login", "ip_address"])

    @staticmethod
    def _clear_login_lock(user):
        user.is_locked = False
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["is_locked", "failed_login_attempts", "locked_until"])

    @staticmethod
    def _is_lock_enabled():
        return settings.LOGIN_LOCK_ENABLED == "True"

    @staticmethod
    def _is_account_locked(user, now):
        return user.is_locked and user.locked_until and user.locked_until > now

    @staticmethod
    def _lock_has_expired(user, now):
        return user.is_locked and user.locked_until and user.locked_until <= now

    @staticmethod
    def request_password_reset(email: str):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return  # don't expose user existence

        token = create_password_reset_token(user.id)
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        EmailService.send_email(
            subject="Password Reset",
            to=[user.email],
            template_name="emails/password_reset.html",
            context={
                "user": user.first_name + " " + user.last_name,
                "reset_link": reset_link,
                "expiry_minutes": 15,
            },
        )

    @staticmethod
    def reset_password(token: str, new_password: str):
        try:
            user_id = decode_password_reset_token(token)
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Invalid token")

        user.set_password(new_password)
        user.save()

    @staticmethod
    def verify_email(token: str):
        try:
            user_id = decode_password_reset_token(token)
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Invalid token")
        user.is_email_verified = True
        user.save()
