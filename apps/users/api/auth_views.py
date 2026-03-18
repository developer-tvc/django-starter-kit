from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from apps.users.api.schemas import (login_schema, logout_schema,
                                    password_reset_confirm_schema,
                                    password_reset_request_schema,
                                    email_verification_schema)
from apps.users.serializers.auth_serializer import (
    LoginSerializer, PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer, EmailVerificationSerializer)
from apps.users.services.auth_service import AuthService


class LoginView(APIView):

    authentication_classes = []  # disables authentication
    permission_classes = []

    @login_schema
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = AuthService.login(
            serializer.validated_data["username"], serializer.validated_data["password"]
        )

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["Auth"])
class CustomTokenBlacklistView(TokenBlacklistView):
    pass


class PasswordResetRequestView(APIView):
    @password_reset_request_schema
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthService.request_password_reset(serializer.validated_data["email"])

        return Response(
            {"message": "If the email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    @password_reset_confirm_schema
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AuthService.reset_password(
                serializer.validated_data["token"],
                serializer.validated_data["new_password"],
            )
            return Response({"message": "Password reset successful"})
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)


class LogoutView(APIView):
    @logout_schema
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)

            # Check if token is already blacklisted
            if BlacklistedToken.objects.filter(token=token).exists():
                return Response(
                    {"detail": "Token already blacklisted"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Blacklist the token
            token.blacklist()
            return Response(
                {"detail": "Logged out successfully"}, status=status.HTTP_200_OK
            )

        except TokenError as e:
            # Expired, malformed, or invalid token
            return Response(
                {"detail": f"Invalid or expired token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
class EmailVerificationView(APIView):
    @email_verification_schema
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AuthService.verify_email(serializer.validated_data["token"])
            return Response({"message": "Email verification successful"})
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)