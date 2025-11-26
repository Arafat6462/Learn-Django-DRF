from rest_framework import permissions


# This file defines custom permission classes for the store application.
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only permissions are allowed for non-admin users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: # Allow read-only access
            return True  # Allow read-only access for all users
        return bool(request.user and request.user.is_staff) # Allow write access only for admin users
    

# Extend DjangoModelPermissions to include 'view' permission for GET requests
# Here overriding the default behavior to add 'view' permissions
class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
