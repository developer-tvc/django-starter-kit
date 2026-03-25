from celery import shared_task
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.models import NotificationLog
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def send_notification_task(self, user_ids, title, message, channels):
    from apps.users.models import User

    users = User.objects.filter(id__in=user_ids)
    service = NotificationService()

    logs = service.send(users, title, message, channels)

    # Celery retry logic
    for log in logs:
        if log.status == "failed" and self.request.retries < self.max_retries:
            try:
                countdown = 10  # seconds
                self.retry(countdown=countdown, exc=Exception(log.payload))
            except self.MaxRetriesExceededError:
                # Mark as permanently failed
                log.status = "failed"
                log.retry_count = self.max_retries
                log.sent_at = timezone.now()
                log.save(update_fields=["status", "retry_count", "sent_at"])
