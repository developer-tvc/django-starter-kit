from django.conf import settings

EMAIL_ENABLED = getattr(settings, "EMAIL_ENABLED", True)
SMS_ENABLED = getattr(settings, "SMS_ENABLED", False)
IN_APP_ENABLED = getattr(settings, "IN_APP_ENABLED", True)
WEBHOOK_ENABLED = getattr(settings, "WEBHOOK_ENABLED", False)
