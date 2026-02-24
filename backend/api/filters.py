import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтрация рецептов по тегам, автору, избранному и корзине.

    Параметры:
        tags: slug тегов (может быть несколько, комбинация ИЛИ)
        author: ID автора
        is_favorited: 1 - только избранные, 0 - все
        is_in_shopping_cart: 1 - только в корзине, 0 - все
    """

    tags = django_filters.filters.BaseInFilter(
        field_name='tags__slug',
        lookup_expr='in'
    )

    author = django_filters.NumberFilter(
        field_name='author__id'
    )

    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты по добавлению в избранное текущего пользователя.
        """
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(favorited_by__user=self.request.user)
            return queryset.none()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты по добавлению в корзину текущего пользователя.
        """
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(in_cart_by__user=self.request.user)
            return queryset.none()
        return queryset
