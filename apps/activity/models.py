from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


class ActivityLog(models.Model):
    
    ACTION_CHOICES = (
        ('create','Create'),
        ('update','Update'),
        ('delete','Delete'),
        ('status','Status')
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True
                            )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey("content_type", "object_id")

    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    