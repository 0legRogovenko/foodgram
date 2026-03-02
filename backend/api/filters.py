import django_filters
from recipes.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтрация рецептов по тегам, автору, избранному и корзине.

    Параметры:
        tags: slug тегов (может быть несколько, комбинация ИЛИ)
        author: ID автора
        is_favorited: 1 - только избранные, 0 - все
        is_in_shopping_cart: 1 - только в корзине, 0 - все
    """

    tags = django_filters.CharFilter(method='filter_tags')

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

    def filter_tags(self, recipes, name, value):
        """Фильтрует рецепты по slug тегов, переданных списком в query params."""
        tags = self.request.query_params.getlist(name)
        if len(tags) == 1 and ',' in tags[0]:
            tags = [tag for tag in tags[0].split(',') if tag]
        if not tags:
            return recipes
        return recipes.filter(tags__slug__in=tags).distinct()

    def filter_is_favorited(self, recipes, name, value):
        """
        Фильтрует рецепты по добавлению в избранное текущего пользователя.
        """
        if value:
            if self.request.user.is_authenticated:
                return recipes.filter(favorite_set__user=self.request.user)
            return recipes.none()
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        """
        Фильтрует рецепты по добавлению в корзину текущего пользователя.
        """
        if value:
            if self.request.user.is_authenticated:
                return recipes.filter(shoppingcart_set__user=self.request.user)
            return recipes.none()
        return recipes


class IngredientFilter(django_filters.FilterSet):
    """Фильтрация ингредиентов по началу названия."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
