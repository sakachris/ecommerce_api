# catalogue/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-created_at',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'created_at')
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
            'fields': ('role','is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )
