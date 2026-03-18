from django.template.loader import render_to_string

from apps.notifications.tasks.email_tasks import send_email_task


class EmailService:

    @staticmethod
    def send_email(subject: str, to: list[str], template_name: str, context: dict):
        """
        Render template + send async email
        """

        body = render_to_string(template_name, context)
        print("ready to go.........")
        for email in to:
            send_email_task.delay(email, subject, body)
