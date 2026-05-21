class SMSService:
    def send(self):
        # SMS delivery is intentionally a no-op here because the project does
        # not define an SMS provider integration yet. NotificationService
        # already guards this call with the SMS_ENABLED feature flag, so this
        # placeholder keeps the interface stable until a provider is added.
        return None
