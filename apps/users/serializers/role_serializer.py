from rest_framework import serializers

from apps.users.models import Role, UserPermission


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPermission
        fields = ["id", "name"]


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ["id", "name"]


class RoleListSerializer(serializers.ModelSerializer):

    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "permissions"]


class RolePermissionAssignSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    permission_ids = serializers.ListField(child=serializers.IntegerField())


class UserRoleAssignSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_ids = serializers.ListField(child=serializers.IntegerField())
