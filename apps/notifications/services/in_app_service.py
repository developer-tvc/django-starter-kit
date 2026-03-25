from apps.notifications.models import Notification


class InAppService:
    def send(self, user, title, message):
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
        )
