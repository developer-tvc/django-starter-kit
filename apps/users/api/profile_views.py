from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.generics.responses import api_response
from apps.users.api import schemas
from apps.users.serializers import profile_serializer
from apps.users.services.profile_service import ProfileService


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @schemas.profile_view_schema
    def get(self, request):
        user = ProfileService.get_profile(request.user)
        serializer = profile_serializer.ProfileViewSerializer(user)
        return api_response(
            message="Profile retrieved successfully.", data=serializer.data
        )

    @schemas.profile_update_schema
    def patch(self, request):
        serializer = profile_serializer.ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = ProfileService.update_profile(request.user, serializer.validated_data)
        serializer = profile_serializer.ProfileViewSerializer(user)
        return api_response(
            message="Profile updated successfully.", data=serializer.data
        )
