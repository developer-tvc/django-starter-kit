from rest_framework import serializers

from apps.users.models import User


class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "avatar_url",
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "avatar_url"]

    def validate(self, attrs):
        if attrs.get("phone_number") and not attrs["phone_number"].isdigit():
            raise serializers.ValidationError(
                {"phone_number": "Phone number must be digits only."}
            )
        return attrs
