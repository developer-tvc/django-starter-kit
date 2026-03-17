from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed


class AuthService:

    @staticmethod
    def login(username: str, password: str):

        user = authenticate(username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid username or password")

        if not user.is_active:
            raise AuthenticationFailed("Account is disabled")

        refresh = RefreshToken.for_user(user)

        return {
            "token_type": "Bearer",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }