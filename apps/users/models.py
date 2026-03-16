from django.db import models
from django.contrib.auth.model import AbstractUser

from generics.mixins import GenericModelMixin




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