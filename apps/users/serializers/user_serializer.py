from rest_framework import serializers

from apps.users.models import Role, User
from apps.users.selectors.role_selectors import get_role_by_name


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active"]
        read_only_fields = ["id"]


class UserCreateSerializer(serializers.Serializer):
    username = serializers.EmailField(max_length=150)
    password = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate(self, attrs):
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "User already exists"})
        return attrs


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
