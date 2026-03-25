import requests


class WebhookService:
    def send(self, user, message):
        requests.post(
            "https://example.com/webhook",
            json={"user_id": user.id, "message": message},
        )
