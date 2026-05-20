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


class AuthService:
    @staticmethod
    def login(username: str, password: str, request):
        user = authenticate(username=username, password=password)
        now = timezone.now()
        get_user = get_user_by_username(username)
        if not get_user:
            raise AuthenticationFailed("Invalid username or password")
        if settings.LOGIN_LOCK_ENABLED == "True":
            # If account is locked and still within lock window
            if (
                get_user.is_locked
                and get_user.locked_until
                and get_user.locked_until > now
            ):
                remaining_seconds = int((get_user.locked_until - now).total_seconds())
                remaining_minutes = remaining_seconds // 60
                remaining_seconds = remaining_seconds % 60
                raise AuthenticationFailed(
                    "Account locked. "
                    f"Try again in {remaining_minutes}m {remaining_seconds}s"
                )

            # If lock time expired → reset lock
            if (
                get_user.is_locked
                and get_user.locked_until
                and get_user.locked_until <= now
            ):
                get_user.is_locked = False
                get_user.failed_login_attempts = 0
                get_user.locked_until = None
                get_user.save(
                    update_fields=["is_locked", "failed_login_attempts", "locked_until"]
                )

        # If lock is disabled but lock time expired → reset lock
        elif (
            settings.LOGIN_LOCK_ENABLED == "False"
            and get_user.is_locked
            and get_user.locked_until
        ):
            get_user.is_locked = False
            get_user.failed_login_attempts = 0
            get_user.locked_until = None
            get_user.save(
                update_fields=["is_locked", "failed_login_attempts", "locked_until"]
            )

        if not user:
            # Password check (already done via authenticate, but kept here if needed)
            if not get_user.check_password(password):
                if settings.LOGIN_LOCK_ENABLED == "True":
                    get_user.failed_login_attempts += 1

                    # Lock account if attempts exceed maximum
                    if int(get_user.failed_login_attempts) >= int(
                        settings.LOGIN_MAX_ATTEMPTS
                    ):
                        get_user.is_locked = True
                        get_user.locked_until = timezone.now() + timedelta(
                            minutes=int(settings.LOGIN_LOCK_MINUTES)
                        )

                    get_user.save(
                        update_fields=[
                            "failed_login_attempts",
                            "is_locked",
                            "locked_until",
                        ]
                    )

            raise AuthenticationFailed("Invalid username or password")
            # Optionally, track failed login globally here
            raise AuthenticationFailed("Invalid username or password")

        if not user.is_active:
            raise AuthenticationFailed("Account is disabled")

        if not user.is_email_verified:
            raise AuthenticationFailed("Account is not verified")

        now = timezone.now()

        # Reset failed attempts on successful login
        if settings.LOGIN_LOCK_ENABLED == "True":
            user.failed_login_attempts = 0
            user.is_locked = False
            user.locked_until = None
            user.save(
                update_fields=["failed_login_attempts", "is_locked", "locked_until"]
            )

        # Update last login and IP
        user.last_login = now
        user.ip_address = get_client_ip(request)
        user.save(update_fields=["last_login", "ip_address"])

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        track_device(request, user)
        return {
            "token_type": "Bearer",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

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
