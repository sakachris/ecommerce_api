# catalogue/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
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
    CategorySerializer,
    ResendEmailVerificationSerializer,
    CustomTokenObtainPairSerializer,
    RegisterAdminSerializer,
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
from .models import Category, Product, ProductImage
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsAdminOrReadOnly
from ecommerce_api.pagination.custom import (
    ProductPagination,
    CategoryPagination,
    ProductImagePagination,
)
from rest_framework import status
from rest_framework.decorators import action
from .throttles import ResendVerificationThrottle

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.exceptions import PermissionDenied

User = get_user_model()
redis_store = RedisTokenStore()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Obtain JWT token",
        operation_description="Authenticate user and obtain JWT token.",
        tags=["Auth - JWT"],
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: openapi.Response(
                description="JWT token obtained successfully.",
                schema=CustomTokenObtainPairSerializer,
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                },
            ),
            400: openapi.Response(
                description="Invalid credentials or account not verified.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "Invalid email or password."
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Override the post method to use the custom serializer.
        """
        return super().post(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    """
    post:
    Register a new user, send verification email.
    """

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

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
    def post(self, request, *args, **kwargs):
        """
        Override the post method to use the custom serializer.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"detail": "User registered successfully. Verification email sent."},
            status=status.HTTP_201_CREATED,
        )
    
class RegisterAdminView(generics.CreateAPIView):
    """
    post:
    Temporary endpoint to register an admin user.
    Only for demonstration and testing purposes.
    """

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterAdminSerializer

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

    @swagger_auto_schema(
        operation_summary="Register an admin user (Temporary Endpoint)",
        operation_description="Create a new admin user account and send a verification email. This endpoint is only temporary and will be disabled soon.",
        tags=["Auth - Registration"],
        request_body=RegisterAdminSerializer,
        responses={
            201: openapi.Response(
                description="Admin registered successfully. Verification email sent.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "Admin registered successfully. Verification email sent."
                    }
                },
            ),
            400: openapi.Response(
                description="Bad request, validation errors.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {
                        "detail": "An admin with that email already exists."
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Override the post method to use the custom serializer.
        """
        if not settings.ENABLE_ADMIN_REGISTRATION:
            raise PermissionDenied("Admin registration is currently disabled.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"detail": "Admin registered successfully. Verification email sent."},
            status=status.HTTP_201_CREATED,
        )


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

    @swagger_auto_schema(
        operation_summary="Verify email (GET)",
        operation_description="Verify user email using the token from query parameters.",
        tags=["Auth - Email Verification"],
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


class ResendVerificationEmailView(APIView):
    """
    post: resend verification email to an unverified user.
    """

    throttle_classes = [ResendVerificationThrottle]
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Resend verification email",
        operation_description="Send a new email verification link to an unverified user.",
        tags=["Auth - Email Verification"],
        request_body=ResendEmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Verification email resent.",
                schema=DetailResponseSerializer,
                examples={"application/json": {"detail": "Verification email resent."}},
            ),
            400: openapi.Response(
                description="Invalid request or user already verified.",
                schema=DetailResponseSerializer,
                examples={
                    "application/json": {"detail": "Email already verified or invalid."}
                },
            ),
        },
    )
    def post(self, request):
        serializer = ResendEmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_active:
            return Response(
                {"detail": "Email already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = EmailVerificationToken.for_user(user)
        redis_store.store(
            token_type=token["token_type"],
            jti=str(token["jti"]),
            ttl=EmailVerificationToken.lifetime,
        )
        verify_path = reverse("auth-verify-email")
        verify_url = f"{settings.PUBLIC_BASE_URL}{verify_path}?token={str(token)}"
        send_verification_email.delay(user.email, verify_url)

        return Response(
            {"detail": "Verification email resent."},
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    get:
    Return the authenticated user's profile.

    patch:
    Update the authenticated user's profile.
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_summary="Get authenticated user profile",
        operation_description="Retrieve the profile of the authenticated user.",
        tags=["Auth - User Profile"],
    )
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Update authenticated user profile",
        operation_description="Update the profile of the authenticated user.",
        tags=["Auth - User Profile"],
        request_body=UserSerializer,
    )
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Replace authenticated user profile",
        operation_description="Replace the profile of the authenticated user.",
        tags=["Auth - User Profile"],
        request_body=UserSerializer,
    )
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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
        tags=["Auth - Password Reset"],
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
        operation_description=(
            "Verify the password reset token from a link (e.g., email link click). "
            "This does not change the password, just verifies the token."
        ),
        tags=["Auth - Password Reset"],
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


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    Provides listing, detail view, and filtering capabilities.
    """

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
    pagination_class = ProductPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve a product with paginated images",
        operation_description="Fetch a single product by ID and include paginated images in the response.",
        tags=["Products"],
        responses={200: ProductDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        product_data = self.get_serializer(product).data

        images = product.images.all()
        paginator = ProductImagePagination()
        paginated_images = paginator.paginate_queryset(images, request)
        image_serializer = ProductImageSerializer(
            paginated_images, many=True, context={"request": request}
        )
        paginated_response = paginator.get_paginated_response(image_serializer.data)

        product_data["images"] = paginated_response.data
        return Response(product_data)

    @swagger_auto_schema(
        operation_summary="Create a new product",
        operation_description="Create a new product entry. Only admins can perform this action.",
        tags=["Products"],
        request_body=ProductDetailSerializer,
        responses={201: ProductDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an existing product",
        operation_description="Fully update a product by its ID. Only admins can perform this action.",
        tags=["Products"],
        request_body=ProductDetailSerializer,
        responses={200: ProductDetailSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a product",
        operation_description="Partially update fields of a product by its ID. Only admins can perform this action.",
        tags=["Products"],
        request_body=ProductDetailSerializer,
        responses={200: ProductDetailSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a product",
        operation_description="Delete a product by its ID. Only admins can perform this action.",
        tags=["Products"],
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List all products",
        operation_description="Retrieve a paginated list of products. Supports filtering by category and price, searching by name and description, and ordering.",
        tags=["Products"],
        responses={200: ProductListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    Provides listing, detail view, and filtering capabilities.
    """
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["name"]
    pagination_class = CategoryPagination
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="Retrieve a paginated list of product categories.",
        tags=["Categories"],
        responses={200: CategorySerializer(many=True)},
    )
    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        category_data = self.get_serializer(category).data

        # Paginate the category’s products
        products = (
            Product.objects.filter(category=category)
            .select_related("category")
            .prefetch_related("images")
        )
        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        product_serializer = ProductListSerializer(
            paginated_products, many=True, context={"request": request}
        )
        paginated_response = paginator.get_paginated_response(product_serializer.data)

        # Inject into main response
        category_data["products"] = paginated_response.data
        return Response(category_data)
    
    @swagger_auto_schema(
        operation_summary="Create a new category",
        operation_description="Create a new product category. Only admins can perform this action.",
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={201: CategorySerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update an existing category",
        operation_description="Fully update a product category by its ID. Only admins can perform this action.",
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={200: CategorySerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update a category",
        operation_description="Partially update fields of a product category by its ID. Only admins can perform this action.",
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={200: CategorySerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete a category",
        operation_description="Delete a product category by its ID. Only admins can perform this action.",
        tags=["Categories"],
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="Retrieve a paginated list of product categories.",
        tags=["Categories"],
        responses={200: CategorySerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing product images.
    """

    queryset = ProductImage.objects.all().select_related("product")
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]
    pagination_class = ProductImagePagination

    @swagger_auto_schema(
        operation_summary="List all product images",
        operation_description="Retrieve a paginated list of product images.",
        tags=["Product Images"],
        responses={200: ProductImageSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve a product image",
        operation_description="Get details of a specific product image by ID.",
        tags=["Product Images"],
        responses={200: ProductImageSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create a new product image",
        operation_description="Upload a new image for a product. Only admins can perform this action.",
        tags=["Product Images"],
        request_body=ProductImageSerializer,
        responses={201: ProductImageSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update an existing product image",
        operation_description="Fully update a product image by its ID. Only admins can perform this action.",
        tags=["Product Images"],
        request_body=ProductImageSerializer,
        responses={200: ProductImageSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update a product image",
        operation_description="Partially update fields of a product image by its ID. Only admins can perform this action.",
        tags=["Product Images"],
        request_body=ProductImageSerializer,
        responses={200: ProductImageSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete a product image",
        operation_description="Delete a product image by its ID. Only admins can perform this action.",
        tags=["Product Images"],
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_summary="Obtain JWT token pair",
        operation_description="Provide email and password to receive access and refresh tokens.",
        tags=["Auth - JWT"],
        request_body=TokenObtainPairSerializer,
        responses={200: TokenObtainPairSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Refresh JWT access token",
        operation_description="Provide refresh token to get a new access token.",
        tags=["Auth - JWT"],
        request_body=TokenRefreshSerializer,
        responses={200: TokenRefreshSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
