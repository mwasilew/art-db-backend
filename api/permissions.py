from rest_framework import permissions
from django.core.exceptions import ImproperlyConfigured


class IsGroupOrAdmin(permissions.BasePermission):
    group_name = None

    def has_permission(self, request, view):

        if not self.group_name:
            raise ImproperlyConfigured(
                "%s needs be configured with 'group_name'" %
                self.__class__.__name__)

        user = request.user
        if user and (user.is_staff or user.is_superuser):
            return True

        return user.groups.filter(name="admin").exists()


class IsAdminGroup(IsGroupOrAdmin):
    group_name = "admin"

