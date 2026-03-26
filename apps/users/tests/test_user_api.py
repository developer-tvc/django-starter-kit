import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from apps.users.tests.factories.user_factory import UserFactory
from apps.users.models import Role, UserPermission, UserRole
from apps.users import constants

def create_user_with_permission(user, permission_name):
    perm, _ = UserPermission.objects.get_or_create(name=permission_name)
    role, _ = Role.objects.get_or_create(name=f"Role_{permission_name}")
    role.permissions.add(perm)
    UserRole.objects.get_or_create(user=user, role=role)

@pytest.mark.django_db
class TestUserCreate:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("user-list-create")
        self.user = UserFactory()
        create_user_with_permission(self.user, constants.USER_CREATE)
        self.client.force_authenticate(user=self.user)

    def test_create_user_success(self):
        payload = {
            "username": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "StrongPass123!"
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == 201
        assert response.data["data"]["username"] == payload["username"]

@pytest.mark.django_db
class TestUserList:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("user-list-create") 
        self.user = UserFactory()
        create_user_with_permission(self.user, constants.USER_VIEW)
        self.client.force_authenticate(user=self.user)

    def test_list_users(self):
        # Create fake users
        UserFactory.create_batch(5)

        response = self.client.get(self.url)

        assert response.status_code == 200
        # 5 created + 1 self.user = 6 users total
        assert len(response.data["data"]) == 6