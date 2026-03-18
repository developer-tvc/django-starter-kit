from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email_task(to_email: str, subject: str, body: str):

    msg = EmailMultiAlternatives(
        subject=subject,
        body="Reset your password using the link.",  # fallback text
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
    )

    msg.attach_alternative(body, "text/html")  # HTML email
    msg.send()
