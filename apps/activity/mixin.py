import threading

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.activity import constants
from apps.activity.models import ActivityLog
from apps.activity.utils import get_diff, serialize_instance


class ActivityMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        is_create = self._state.adding
        old_instance = None if is_create else self.__class__.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        user = self._get_activity_user()
        if not user:
            return

        ct = ContentType.objects.get_for_model(self)
        label = self._get_activity_label()

        if is_create:
            self._log_create_activity(user, ct, label)
            return

        self._log_update_activity(user, ct, label, old_instance)

    @staticmethod
    def _get_activity_user():
        user = getattr(threading.current_thread(), "_django_user", None)
        if isinstance(user, AnonymousUser):
            return None
        return user

    def _get_activity_label(self):
        model_name = self.__class__.__name__
        return constants.LOG_DESCRIPTION.get(model_name, model_name.lower())

    def _log_create_activity(self, user, content_type, label):
        ActivityLog.objects.create(
            user=user,
            action=f"{label} created",
            content_type=content_type,
            object_id=self.pk,
            description=f"created by {user.first_name} {user.last_name}",
            new_value=serialize_instance(self),
        )

    def _log_update_activity(self, user, content_type, label, old_instance):
        diff = get_diff(old_instance, self)
        if not diff:
            return

        action = f"{label} updated"
        changes = self._build_change_messages(diff)
        description = (
            f"{action} by {user.first_name} {user.last_name}. "
            f"Changes: {'; '.join(changes)}"
        )

        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=self.pk,
            old_value=diff["old"],
            new_value=diff["new"],
            description=description,
        )

    def _build_change_messages(self, diff):
        changes = []

        for field in diff["new"]:
            old = diff["old"].get(field)
            new = diff["new"].get(field)
            if self._is_empty_activity_value(old) and not self._is_empty_activity_value(
                new
            ):
                changes.append(f"added {field} → {new}")
            elif not self._is_empty_activity_value(
                old
            ) and self._is_empty_activity_value(new):
                changes.append(f"removed {field} (was {old})")
            elif old != new:
                changes.append(f"changed {field} from {old} → {new}")

        return changes

    @staticmethod
    def _is_empty_activity_value(value):
        return (
            value is None
            or value == "None"
            or value == ""
            or value == []
            or value == {}
        )

    def delete(self, *args, **kwargs):
        user = getattr(threading.current_thread(), "_django_user", None)
        if isinstance(user, AnonymousUser):
            user = None

        ct = ContentType.objects.get_for_model(self)
        model_name = self.__class__.__name__
        label = constants.LOG_DESCRIPTION.get(model_name, model_name.lower())

        # Serialize the instance before deleting
        old_value = serialize_instance(self)

        # Create activity log
        if user:
            ActivityLog.objects.create(
                user=user,
                action=f"{label} deleted",
                content_type=ct,
                object_id=self.pk,
                old_value=old_value,
                new_value=None,
                description=f"{label} deleted by {user.first_name} {user.last_name}",
            )

        # Delete the instance
        super().delete(*args, **kwargs)
