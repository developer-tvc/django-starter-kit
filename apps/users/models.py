from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from apps.generics.mixins import GenericModelMixin
from django.conf import settings

class User(AbstractUser):
    # Changing default username field type `CharField` to `EmailField`
    username = models.EmailField(_('email address'), unique=True, error_messages={
                                 'unique': "A user with that username already exists."})

    EMAIL_FIELD = 'username'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name_plural = "Users"


class UserPermission(GenericModelMixin):
    """
    Custom permission table for fine-grained access control.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Role(GenericModelMixin):
    """
    Custom role table.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(UserPermission, blank=True, related_name="roles")

    def __str__(self):
        return self.name


class UserRole(GenericModelMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "role")