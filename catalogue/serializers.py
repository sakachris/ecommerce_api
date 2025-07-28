# catalogue/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserRole, Category, Product, ProductImage
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image_id", "image_url", "is_primary"]


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
    images = ProductImageSerializer(many=True, read_only=True)
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
            "images",
        ]


# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             "product_id",
#             "category",
#             "name",
#             "description",
#             "price",
#             "stock_quantity",
#             "created_at",
#             "updated_at",
#             "images",
#         ]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name", "description", "created_at"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["category_id", "name", "description", "created_at", "products"]