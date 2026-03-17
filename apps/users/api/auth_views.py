from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.users.serializers.auth_serializer import LoginSerializer
from apps.users.services.auth_service import AuthService
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from apps.users.api.schemas import login_schema


class LoginView(APIView):

    authentication_classes = [] #disables authentication    
    permission_classes = []
    @login_schema
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = AuthService.login(
            serializer.validated_data["username"],
            serializer.validated_data["password"]
        )

        return Response(tokens, status=status.HTTP_200_OK)



@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["Auth"])
class CustomTokenBlacklistView(TokenBlacklistView):
    pass