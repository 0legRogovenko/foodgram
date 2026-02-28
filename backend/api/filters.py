import django_filters
from django.contrib import admin

from recipes.models import Recipe
from recipes.constants import CHOICES_YES_NO


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

        fast_params = {'cooking_time__range': (0, fast_threshold)}
        medium_params = {'cooking_time__range': (
            fast_threshold, medium_threshold)}
        slow_params = {'cooking_time__range': (medium_threshold, times[-1])}

        fast_count = recipes.filter(**fast_params).count()
        medium_count = recipes.filter(**medium_params).count()
        slow_count = recipes.filter(**slow_params).count()

        return [
            ('fast', f'Быстрые ({fast_count})'),
            ('medium', f'Средние ({medium_count})'),
            ('slow', f'Медленные ({slow_count})'),
        ]

    def queryset(self, request, recipes):
        value = self.value
        if not value:
            return recipes

        parts = value.split('-')
        key = parts[0]

        ranges = {
            'fast': (0, int(parts[1])),
            'medium': (int(parts[1]), int(parts[2])),
            'slow': (int(parts[1]), recipes.order_by(
                '-cooking_time'
            ).first().cooking_time),
        }

        params = {'cooking_time__range': ranges[key]}
        return recipes.filter(**params)


class BaseYesNoFilter(admin.SimpleListFilter):
    """Базовый фильтр для yes/no логики."""

    title = None
    parameter_name = None
    field_name = None

    def lookups(self, request, model_admin):
        return CHOICES_YES_NO

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(**{self.field_name: False}).distinct()
        elif self.value() == 'no':
            return queryset.filter(**{self.field_name: True}).distinct()
        return queryset


class HasRecipesFilter(BaseYesNoFilter):
    """Фильтр 'есть рецепты'."""

    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    field_name = 'recipes__isnull'


class HasSubscriptionsFilter(BaseYesNoFilter):
    """Фильтр 'есть подписки'."""

    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    field_name = 'subscriptions__isnull'


class HasSubscribersFilter(BaseYesNoFilter):
    """Фильтр 'есть подписчики'."""

    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'
    field_name = 'subscribers__isnull'


class HasInRecipesFilter(BaseYesNoFilter):
    """Фильтр 'есть в рецептах'."""

    title = 'Есть в рецептах'
    parameter_name = 'has_in_recipes'
    field_name = 'ingredient_in_recipes__isnull'
