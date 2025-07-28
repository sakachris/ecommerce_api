# catalogue/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    DetailResponseSerializer,
    VerifyEmailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CategoryListSerializer,
    CategoryDetailSerializer,
)
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError
from .tokens import EmailVerificationToken, PasswordResetToken
from .tasks import send_verification_email, send_password_reset_email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .redis_token_store import RedisTokenStore
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsAdminOrReadOnly


User = get_user_model()
redis_store = RedisTokenStore()


class RegisterView(generics.CreateAPIView):
    """
    post:
    Register a new user, send verification email.
    """

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Create a new user account and send a verification email.",
        tags=["Auth - Registration"],
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully. Verification email sent.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "User registered successfully. Verification email sent."
                    }
                },
            ),
            400: openapi.Response(
                description="Bad request, validation errors.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "A user with that email already exists."
                    }
                },
            ),
        },
    )
    def perform_create(self, serializer):
        user = serializer.save()
        token = EmailVerificationToken.for_user(user)

        # Store jti with TTL in Redis
        redis_store.store(
            token_type=token["token_type"],
            jti=str(token["jti"]),
            ttl=EmailVerificationToken.lifetime,
        )

        verify_path = reverse("auth-verify-email")
        verify_url = f"{settings.PUBLIC_BASE_URL}{verify_path}?token={str(token)}"
        send_verification_email.delay(user.email, verify_url)


class VerifyEmailView(APIView):
    permission_classes = (permissions.AllowAny,)
    """    get:
    Verify user email using the token from query parameters.
    post:
    Verify user email using the token from request body.
    """

    def _verify_token(self, token):
        try:
            payload = UntypedToken(token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payload.get("token_type") != "email":
            return Response(
                {"detail": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST
            )

        jti = str(payload.get("jti"))
        user_id = payload.get("user_id")

        if not redis_store.pop("email", jti):
            return Response(
                {"detail": "Token already used or not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user.is_active:
            return Response(
                {"detail": "Email already verified"}, status=status.HTTP_200_OK
            )

        user.is_active = True
        user.save()
        return Response(
            {"detail": "Email verified successfully"}, status=status.HTTP_200_OK
        )

    def get(self, request, *args, **kwargs):
        data = {"token": request.query_params.get("token")}
        serializer = VerifyEmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return self._verify_token(serializer.validated_data["token"])

    @swagger_auto_schema(
        operation_summary="Verify email (POST)",
        operation_description="Verify user email using the provided token.",
        tags=["Auth - Email Verification"],
        request_body=VerifyEmailSerializer,
        responses={
            200: openapi.Response(
                description="Email verified successfully.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {"detail": "Email verified successfully."}
                },
            ),
            400: openapi.Response(
                description="Invalid or expired token.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "Invalid or expired token."}},
            ),
            404: openapi.Response(
                description="User not found.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "User not found."}},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._verify_token(serializer.validated_data["token"])


class MeView(generics.RetrieveUpdateAPIView):
    """
    get:
    Return the authenticated user's profile.

    patch:
    Update the authenticated user's profile.
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Get authenticated user profile",
        operation_description="Retrieve the profile of the authenticated user.",
        tags=["Auth - User Profile"],
        responses={
            200: openapi.Response(
                description="User profile retrieved successfully.",
                schema=UserSerializer,
            ),
            401: openapi.Response(
                description="Authentication credentials were not provided.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                },
            ),
        },
    )
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    post:
    Change password for the authenticated user.
    """

    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="Change the authenticated user's password.",
        tags=["Auth - Password Management"],
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password updated successfully.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {"detail": "Password updated successfully."}
                },
            ),
            400: openapi.Response(
                description="Invalid old password or bad payload.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "Old password is incorrect."}},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    """
    post:
    Request a password reset email for the user.
    """

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        operation_summary="Request password reset",
        operation_description=(
            "Send a password reset email to the user. "
            "A JWT-based password reset token will be embedded in the link."
        ),
        tags=["Auth - Password Reset"],
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="Password reset email sent.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "Password reset email sent."}},
            ),
            400: openapi.Response(
                description="Invalid email or payload.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "No user found with this email address."
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.get(email=email)
        token = PasswordResetToken.for_user(user)

        redis_store.store(
            token_type=token["token_type"],
            jti=str(token["jti"]),
            ttl=PasswordResetToken.lifetime,
        )

        reset_path = reverse("auth-reset-password-confirm")
        reset_url = f"{settings.PUBLIC_BASE_URL}{reset_path}?token={str(token)}"
        send_password_reset_email.delay(user.email, reset_url)
        return Response(
            {"detail": "Password reset email sent."}, status=status.HTTP_200_OK
        )


# class PasswordResetConfirmView(APIView):
#     """
#     post:
#     Confirm password reset with the token and set a new password.
#     """
#     permission_classes = (permissions.AllowAny,)

#     @swagger_auto_schema(
#         operation_summary="Confirm password reset",
#         operation_description=(
#             "Confirm password reset with the token and set a new password."
#         ),
#         tags=["Auth - Password Reset"],
#         request_body=PasswordResetConfirmSerializer,
#         responses={
#             200: openapi.Response(
#                 description="Password reset successful.",
#                 schema=DetailResponseSerializer,
#                 examples={"application/json": {"detail": "Password reset successful."}},
#             ),
#             400: openapi.Response(
#                 description="Invalid or expired token / bad payload.",
#                 schema=DetailResponseSerializer,
#                 examples={"application/json": {"detail": "Invalid or expired token."}},
#             ),
#             404: openapi.Response(
#                 description="User not found.",
#                 schema=DetailResponseSerializer,
#                 examples={"application/json": {"detail": "User not found."}},
#             ),
#         },
#     )

#     def post(self, request, *args, **kwargs):
#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         token = serializer.validated_data['token']
#         new_password = serializer.validated_data['new_password']

#         try:
#             payload = UntypedToken(token)
#         except TokenError:
#             return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

#         if payload.get('token_type') != 'password_reset':
#             return Response({"detail": "Invalid token type."}, status=status.HTTP_400_BAD_REQUEST)

#         jti = str(payload.get('jti'))
#         user_id = payload.get('user_id')

#         # Atomically pop from Redis => one-time use
#         if not redis_store.pop('password_reset', jti):
#             return Response({"detail": "Token already used or not found."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(user_id=user_id)
#         except User.DoesNotExist:
#             return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

#         user.set_password(new_password)
#         user.save()
#         return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    post:
    Confirm password reset with the token and set a new password.

    get:
    Verify password reset token from a link (e.g., email link click).
    """

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        operation_summary="Confirm password reset (POST)",
        operation_description="Reset password using token and new password.",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successful.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "Password reset successful."}},
            ),
            400: openapi.Response(
                description="Invalid or expired token / bad payload.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "Invalid or expired token."}},
            ),
            404: openapi.Response(
                description="User not found.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "User not found."}},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        return self._verify_token_and_reset_password(token, new_password)

    @swagger_auto_schema(
        operation_summary="Verify password reset token (GET)",
        manual_parameters=[
            openapi.Parameter(
                "token",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="Password reset token",
                example="eyJ0eXAiOiJKV1QiLCJh...",
            )
        ],
        responses={
            200: openapi.Response(description="Token is valid. You may proceed."),
            400: openapi.Response(description="Invalid or expired token."),
        },
    )
    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"detail": "Token query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self._verify_token_and_reset_password(
            token, new_password=None, dry_run=True
        )

    def _verify_token_and_reset_password(self, token, new_password=None, dry_run=False):
        try:
            payload = UntypedToken(token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payload.get("token_type") != "password_reset":
            return Response(
                {"detail": "Invalid token type."}, status=status.HTTP_400_BAD_REQUEST
            )

        jti = str(payload.get("jti"))
        user_id = payload.get("user_id")

        # Only consume token if this is not a dry run
        if not dry_run and not redis_store.pop("password_reset", jti):
            return Response(
                {"detail": "Token already used or not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if dry_run:
            return Response({"detail": "Token is valid."}, status=status.HTTP_200_OK)

        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password reset successful."}, status=status.HTTP_200_OK
        )


# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["name"]


# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = (
#         Product.objects.select_related("category").prefetch_related("images").all()
#     )
#     serializer_class = ProductSerializer
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#     ]
#     filterset_fields = ["category", "price"]
#     search_fields = ["name", "description"]
#     ordering_fields = ["price", "created_at"]
#     ordering = ["-created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.all().select_related("category").prefetch_related("images")
    )
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "price"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategoryListSerializer
