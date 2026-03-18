from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from apps.generics.utils.token_utils import (create_password_reset_token,
                                             decode_password_reset_token)
from apps.notifications.services.email_service import EmailService

User = get_user_model()


class AuthService:

    @staticmethod
    def login(username: str, password: str):

        user = authenticate(username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid username or password")

        if not user.is_active:
            raise AuthenticationFailed("Account is disabled")
        if not user.is_email_verified:
            raise AuthenticationFailed("Account is not verified")
        refresh = RefreshToken.for_user(user)

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
