from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение для автора рецепта.

    Разрешает безопасные методы (GET, HEAD, OPTIONS) для всех,
    а методы изменения (POST, PUT, PATCH, DELETE) только для автора.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет разрешение на уровне объекта.

        Args:
            request: HTTP запрос.
            view: View объект.
            obj: Проверяемый объект (рецепт).

        Returns:
            bool: True если доступ разрешен, False иначе.
        """
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return obj.author == request.user
