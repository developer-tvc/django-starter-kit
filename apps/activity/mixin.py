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
        old_instance = None

        if not is_create:
            old_instance = self.__class__.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        user = getattr(threading.current_thread(), "_django_user", None)
        if isinstance(user, AnonymousUser):
            user = None

        if not user:
            return

        if not user:
            return

        ct = ContentType.objects.get_for_model(self)

        model_name = self.__class__.__name__

        label = constants.LOG_DESCRIPTION.get(model_name, model_name.lower())

        if is_create:
            ActivityLog.objects.create(
                user=user,
                action=f"{label} created",
                content_type=ct,
                object_id=self.pk,
                description=f"created by {user.first_name} {user.last_name}",
                new_value=serialize_instance(self),
            )
        elif not is_create:
            action = f"{label} updated"
            diff = get_diff(old_instance, self)
            if not diff:
                return
            changes = []

            def is_empty(value):
                return (
                    value is None
                    or value == "None"
                    or value == ""
                    or value == []
                    or value == {}
                )

            for field in diff["new"].keys():
                old = diff["old"].get(field)
                new = diff["new"].get(field)
                if is_empty(old) and not is_empty(new):
                    changes.append(f"added {field} → {new}")
                elif not is_empty(old) and is_empty(new):
                    changes.append(f"removed {field} (was {old})")
                elif old != new:
                    changes.append(f"changed {field} from {old} → {new}")

            description = f"{action} by {user.first_name} {user.last_name}. Changes: {'; '.join(changes)}"

            ActivityLog.objects.create(
                user=user,
                action=action,
                content_type=ct,
                object_id=self.pk,
                old_value=diff["old"],
                new_value=diff["new"],
                description=description,
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
