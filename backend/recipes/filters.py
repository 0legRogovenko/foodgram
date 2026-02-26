import django_filters
from django.contrib import admin

from .models import Recipe


class CookingTimeFilter(admin.SimpleListFilter):
    """Фильтр по времени готовки с динамическими порогами."""

    title = 'Время готовки'
    parameter_name = 'cooking_time_range'

    def lookups(self, request, model_admin):
        recipes = Recipe.objects.all()
        if not recipes.exists():
            return []

        times = sorted(recipes.values_list('cooking_time', flat=True))
        fast_threshold = times[len(times) // 3]
        medium_threshold = times[2 * len(times) // 3]

        fast_count = recipes.filter(cooking_time__lt=fast_threshold).count()
        medium_count = recipes.filter(
            cooking_time__gte=fast_threshold,
            cooking_time__lt=medium_threshold
        ).count()
        slow_count = recipes.filter(
            cooking_time__gte=medium_threshold
        ).count()

        return (
            (f'fast_{fast_threshold}',
             f'Быстрее {fast_threshold} мин ({fast_count})'),
            (f'medium_{fast_threshold}_{medium_threshold}',
             f'{fast_threshold}-{medium_threshold} мин ({medium_count})'),
            (f'slow_{medium_threshold}',
             f'Долго (более {medium_threshold} мин) ({slow_count})'),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value().startswith('fast'):
            threshold = int(self.value().split('_')[1])
            return queryset.filter(cooking_time__lt=threshold)
        elif self.value() and self.value().startswith('medium'):
            parts = self.value().split('_')
            start = int(parts[1])
            end = int(parts[2])
            return queryset.filter(
                cooking_time__gte=start, cooking_time__lt=end
            )
        elif self.value() and self.value().startswith('slow'):
            threshold = int(self.value().split('_')[1])
            return queryset.filter(cooking_time__gte=threshold)
        return queryset


class HasRecipesFilter(admin.SimpleListFilter):
    """Фильтр 'есть рецепты'."""

    title = 'Есть рецепты'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(recipes__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(recipes__isnull=True).distinct()
        return queryset


class HasSubscriptionsFilter(admin.SimpleListFilter):
    """Фильтр 'есть подписки'."""

    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(subscriptions__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(subscriptions__isnull=True).distinct()
        return queryset


class HasSubscribersFilter(admin.SimpleListFilter):
    """Фильтр 'есть подписчики'."""

    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(subscribers__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(subscribers__isnull=True).distinct()
        return queryset


class HasInRecipesFilter(admin.SimpleListFilter):
    """Фильтр 'есть в рецептах'."""

    title = 'Есть в рецептах'
    parameter_name = 'has_in_recipes'

    def lookups(self, request, model_admin):
        return (('yes', 'Да'), ('no', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                ingredient_in_recipes__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(
                ingredient_in_recipes__isnull=True).distinct()
        return queryset


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
