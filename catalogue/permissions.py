from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admin users to edit/delete, while others can only read.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS: GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can read
        return request.user and request.user.is_staff  # Only admin (is_staff=True) can write
