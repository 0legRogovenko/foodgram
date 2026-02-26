from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение для автора рецепта.

    Разрешает безопасные методы (GET, HEAD, OPTIONS) для всех,
    а методы изменения (POST, PUT, PATCH, DELETE) только для автора.
    """

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешение на уровне объекта."""
        return request.method in SAFE_METHODS or obj.author == request.user
