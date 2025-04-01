from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Права доступа для администратора."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Изменения только для администратора.

    Разрешает безопасные методы для всех пользователей.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    """
    Изменения доступны владельцу, модератору или администратору.

    Разрешает безопасные методы для всех пользователей.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
            )
        )
