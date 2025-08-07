from rest_framework import permissions

class IsStoreManager(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'store_manager' role to access a view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'store_manager' role.
        return request.user and request.user.is_authenticated and request.user.role == 'store_manager'