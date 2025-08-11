# catalogue/tasks.py
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(
        bind=True, max_retries=3, default_retry_delay=30, queue='ecommerce'
    )
def send_verification_email(
    self, to_email: str, verification_url: str, full_name: str = None
):
    """
    Task to send email verification link to the user.
    Args:
        to_email (str): The email address to send the verification link.
        verification_url (str): The URL for email verification.
        full_name (str, optional): Full name of the user for personalization.
    """
    try:
        subject = "Verify your email address"
        message = (
            f"Dear {full_name or 'User'},\n\nPlease click the link below "
            f"to verify your email:\n{verification_url}\n\nThank you!"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
        bind=True, max_retries=3, default_retry_delay=30, queue='ecommerce'
    )
def send_password_reset_email(
    self, to_email: str, reset_url: str, full_name: str = None
):
    """
    Task to send password reset link to the user.
    Args:
        to_email (str): The email address to send the reset link.
        reset_url (str): The URL for password reset.
        full_name (str, optional): Full name of the user for personalization.
    """
    try:
        subject = "Password Reset Request"
        message = (
            f"Dear {full_name or 'User'},\n\nWe received a "
            f"password reset request for your account.\n"
            f"Click the link below to reset your password:\n{reset_url}\n\n"
            f"If you did not request this, you can ignore this email."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
        bind=True, max_retries=3, default_retry_delay=30, queue='ecommerce'
    )
def send_account_deleted_email(self, to_email: str, full_name: str = None):
    """
    Task to send account deletion confirmation email.
    Args:
        to_email (str): The email address to send the deletion confirmation.
        full_name (str, optional): Full name of the user for personalization.
    """
    try:
        subject = "Your account has been deleted"
        message = (
            f"Dear {full_name or 'User'},\n\n"
            "Your account has been permanently deleted from our system. "
            "If this was not you, please contact support immediately."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False
        )
    except Exception as exc:
        raise self.retry(exc=exc)
