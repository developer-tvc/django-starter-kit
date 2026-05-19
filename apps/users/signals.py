from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.generics.utils.token_utils import create_password_reset_token
from apps.notifications.services.email_service import EmailService
from apps.users.models import User


@receiver(post_save, sender=User)
def send_verification_email(sender, instance: User, created, **kwargs):
    """
    Send verification email when a new user is created.
    """
    if not settings.EMAIL_VERIFICATION_ENABLED:
        return
    if created:
        # Generate a verification token
        token = create_password_reset_token(instance.id)
        verification_link = f"http://localhost:3000/verify-account?token={token}"
        EmailService.send_email(
            subject="Account Verification",
            to=[instance.email],
            template_name="emails/account_verification.html",
            context={
                "user": instance.first_name + " " + instance.last_name,
                "verification_link": verification_link,
                "expiry_minutes": 15,
            },
        )
