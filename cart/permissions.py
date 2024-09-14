from rest_framework import permissions
from accounts.models import User


class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers to access the cart.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.CUSTOMER
