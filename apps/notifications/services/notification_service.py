from django.utils import timezone
from apps.notifications.constants import SMS_ENABLED, IN_APP_ENABLED, WEBHOOK_ENABLED
from apps.notifications.models import NotificationLog
from apps.notifications.services.sms_service import SMSService
from apps.notifications.services.in_app_service import InAppService
from apps.notifications.services.webhook_service import WebhookService


class NotificationService:

    def __init__(self):
        self.sms_service = SMSService()
        self.in_app_service = InAppService()
        self.webhook_service = WebhookService()

    def send(self, users, title, message, channels: list):
        logs = []

        for user in users:
            for channel in channels:
                log = NotificationLog.objects.create(
                    user=user,
                    type=channel,
                    title=title,
                    message=message,
                    status="pending",
                    retry_count=0,
                )
                logs.append(log)

            try:
                if channel == "sms" and SMS_ENABLED:
                    self.sms_service.send(user, message)
                elif channel == "in_app" and IN_APP_ENABLED:
                    self.in_app_service.send(user, title, message)
                elif channel == "webhook" and WEBHOOK_ENABLED:
                    self.webhook_service.send(user, message)

                # Mark success
                log.status = "sent"
                log.sent_at = timezone.now()
                log.save(update_fields=["status", "sent_at"])

            except Exception as e:
                # Mark failure and store exception for retry/debug
                log.status = "failed"
                log.retry_count += 1
                log.payload = {"error": str(e)}
                log.save(update_fields=["status", "retry_count", "payload"])

        return logs
