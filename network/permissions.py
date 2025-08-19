from rest_framework import permissions


class IsActiveStaff(permissions.BasePermission):
    """
    Разрешает доступ только аутентифицированным,
    активным пользователям с правами staff.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )
