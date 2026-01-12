from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Кастомный пермишен для проверки владельца объекта
    Задание 2: Только владелец может изменять или удалять объект
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для остальных методов проверяем, что пользователь - владелец
        return obj.owner == request.user


class IsTaskOwner(permissions.BasePermission):
    """
    Пермишен для проверки, что пользователь владелец задачи
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSubTaskOwner(permissions.BasePermission):
    """
    Пермишен для проверки, что пользователь владелец подзадачи
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user