from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users (including superusers).
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())

class IsTechnicianUser(BasePermission):
    """
    Allows access only to technician users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Technician').exists()

class IsSecretaryUser(BasePermission):
    """
    Allows access only to secretary users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Secretary').exists()

class IsAdminOrTechnicianReadOnly(BasePermission):
    """
    The request is authenticated as an admin, or is a read-only request for a technician.
    """
    def has_permission(self, request, view):
        is_admin = request.user and (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())
        is_technician = request.user and request.user.groups.filter(name='Technician').exists()

        if is_admin:
            return True

        if is_technician and request.method in SAFE_METHODS:
            return True

        return False

class IsAdminOrSecretaryOrTechnicianCreateOrReadOnly(BasePermission):
    """
    Allows full access to Admin and Secretary users.
    Allows create and read-only access to Technician users.
    """
    def has_permission(self, request, view):
        is_admin = request.user and (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())
        is_secretary = request.user and request.user.groups.filter(name='Secretary').exists()
        is_technician = request.user and request.user.groups.filter(name='Technician').exists()

        if is_admin or is_secretary:
            return True

        if is_technician:
            if request.method in SAFE_METHODS or request.method == 'POST':
                return True

        return False

class IsAdminOrTechnicianCreateOrReadOnly(BasePermission):
    """
    The request is authenticated as an admin, or is a create or read-only request for a technician.
    """
    def has_permission(self, request, view):
        is_admin = request.user and (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())
        is_technician = request.user and request.user.groups.filter(name='Technician').exists()

        if is_admin:
            return True

        if is_technician:
            if request.method in SAFE_METHODS or request.method == 'POST':
                return True

        return False

class IsAdminOrSecretaryOrTechnicianReadOnly(BasePermission):
    """
    Allows full access to Admin and Secretary users.
    Allows read-only access to Technician users.
    """
    def has_permission(self, request, view):
        is_admin = request.user and (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())
        is_secretary = request.user and request.user.groups.filter(name='Secretary').exists()
        is_technician = request.user and request.user.groups.filter(name='Technician').exists()

        if is_admin or is_secretary:
            return True

        if is_technician and request.method in SAFE_METHODS:
            return True

        return False