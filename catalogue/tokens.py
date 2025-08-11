# catalogue/tokens.py
from django.conf import settings
from rest_framework_simplejwt.tokens import Token


class EmailVerificationToken(Token):
    token_type = 'email'
    lifetime = settings.EMAIL_VERIFICATION_TOKEN_LIFETIME

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        return token


class PasswordResetToken(Token):
    token_type = 'password_reset'
    lifetime = settings.PASSWORD_RESET_TOKEN_LIFETIME
