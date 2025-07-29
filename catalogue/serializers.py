# catalogue/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserRole, Category, Product, ProductImage
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get(self.username_field)
        password = attrs.get('password')

        try:
            user = User.objects.get(**{self.username_field: email})
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not check_password(password, user.password):
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "Account not verified. Please check your email for the verification link or request a new one.",
                "unverified": True,
                "resend_endpoint": "/api/auth/resend-verification/"
            })

        # now that the user is verified, let the default serializer generate the token
        data = super().validate(attrs)
        return data


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_("A user with that email already exists."),
            )
        ],
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "password",
        )
        read_only_fields = ("user_id", "role")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number"),
            is_active=False,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "created_at",
        )
        read_only_fields = ("user_id", "email", "role", "created_at")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)


class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True, help_text="JWT email verification token"
    )

from rest_framework import serializers

class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = ["image_id", "image_url", "is_primary"]


class ProductImageSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            "image_id",
            "product",         # Required when creating or updating
            "product_name",    # Read-only display
            "image_url",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["image_id", "created_at", "updated_at", "product_name"]

    def validate(self, data):
        """
        Ensure only one primary image per product.
        """
        is_primary = data.get("is_primary", False)
        product = data.get("product")

        # When updating, exclude self from the check
        instance = getattr(self, "instance", None)
        if is_primary and product:
            existing_primary = ProductImage.objects.filter(
                product=product,
                is_primary=True
            )
            if instance:
                existing_primary = existing_primary.exclude(pk=instance.pk)

            if existing_primary.exists():
                raise serializers.ValidationError(
                    {"is_primary": "This product already has a primary image."}
                )

        return data


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "name",
            "price",
            "category",
            "category_name",
            "primary_image",
        ]

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        return primary.image_url if primary else None

class ProductDetailSerializer(serializers.ModelSerializer):
    # images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "category",
            "category_name",
            "name",
            "description",
            "price",
            "stock_quantity",
            "created_at",
            "updated_at",
            # "images",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name", "description", "created_at"]


# class CategoryDetailSerializer(serializers.ModelSerializer):
#     products = ProductListSerializer(many=True, read_only=True)

#     class Meta:
#         model = Category
#         fields = ["category_id", "name", "description", "created_at", "products"]