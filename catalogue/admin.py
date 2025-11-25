# catalogue/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    BlockedIP,
    Category,
    Product,
    ProductImage,
    RequestLog,
    User
)
from .models import Review


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    Allows management of user accounts with custom fields.
    """
    ordering = ('-created_at',)
    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_staff',
        'created_at'
    )
    list_filter = (
        'role', 'is_staff', 'is_superuser', 'is_active', 'created_at'
    )
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'role',
                'is_staff',
                'is_superuser'
            ),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing product categories.
    Allows CRUD operations on categories.
    """
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing products.
    Allows CRUD operations on products, including category management.
    """
    list_display = (
        'name',
        'category',
        'price',
        'stock_quantity',
        'created_at',
        'updated_at'
    )
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('created_at', 'updated_at')
        return self.readonly_fields


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing product images.
    Allows CRUD operations on product images.
    """
    list_display = ('product', 'image', 'is_primary', 'created_at')
    list_filter = ('is_primary',)
    search_fields = ('product__name',)
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """
    Admin interface for managing request logs.
    Allows viewing of logged requests with details.
    """
    list_display = ('ip_address', 'path', 'timestamp', 'country', 'city')
    ordering = ('-timestamp',)


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    """
    Admin interface for managing blocked IP addresses.
    Allows viewing and managing IP addresses that are blocked.
    """
    list_display = ('ip_address',)
    ordering = ('ip_address',)
    search_fields = ('ip_address',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for product reviews.
    """
    list_display = ("review_id", "product", "user", "rating", "created_at", "updated_at")
    list_filter = ("rating",)
    search_fields = ("product__name", "user__email", "comment")
    ordering = ("-created_at",)
    raw_id_fields = ("product", "user")
