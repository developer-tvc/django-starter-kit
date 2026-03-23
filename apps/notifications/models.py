from apps.generics.mixins import GenericModelMixin
from django.db import models

class NotificationLog(GenericModelMixin):

    TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("in_app", "In App"),
        ("webhook", "Webhook"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    retry_count = models.IntegerField(default=0)

    payload = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)


class Notification(GenericModelMixin):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)