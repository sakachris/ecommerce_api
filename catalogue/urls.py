# catalogue/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ChangePasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProductImageViewSet,
    ProductViewSet,
    ReviewViewSet,
    ProfileView,
    RegisterAdminView,
    RegisterView,
    ResendVerificationEmailView,
    VerifyEmailView
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="products")
router.register(
    r"product-images", ProductImageViewSet, basename="productimage"
)
router.register(r"reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path(
        "auth/register-admin/",
        RegisterAdminView.as_view(),
        name="auth-register-admin"
    ),
    path(
        "auth/verify-email/",
        VerifyEmailView.as_view(),
        name="auth-verify-email"
    ),
    path(
        "auth/resend-email/",
        ResendVerificationEmailView.as_view(),
        name="auth-resend-email"
    ),
    path(
        'auth/login/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path("auth/profile/", ProfileView.as_view(), name="auth-profile"),
    path(
        "auth/change-password/",
        ChangePasswordView.as_view(),
        name="auth-change-password",
    ),
    path(
        "auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="auth-reset-password",
    ),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="auth-reset-password-confirm",
    ),
    # JWT
    path(
        "auth/token/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path("", include(router.urls)),
]

