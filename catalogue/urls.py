# catalogue/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, MeView, ChangePasswordView, VerifyEmailView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='auth-reset-password'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-reset-password-confirm'),

    # JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]