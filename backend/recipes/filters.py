from django.contrib import admin

from .models import Recipe


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time_range'
    ranges = {}

    def lookups(self, request, model_admin):
        times = list(
            Recipe.objects.order_by(
                'cooking_time'
            ).values_list('cooking_time', flat=True).distinct()
        )
        if len(times) < 3:
            return ()

        fast_threshold = times[len(times) // 3]
        medium_threshold = times[2 * len(times) // 3]

        self.ranges = {
            'fast': (0, fast_threshold),
            'medium': (fast_threshold, medium_threshold),
            'slow': (medium_threshold, max(times)),
        }

        return (
            ('fast', f'Быстрее {fast_threshold} мин'),
            ('medium', f'{fast_threshold}-{medium_threshold} мин'),
            ('slow', f'Дольше {medium_threshold} мин'),
        )

    def queryset(self, request, recipes):
        if self.value() not in self.ranges:
            return recipes

        return recipes.filter(
            cooking_time__range=self.ranges[self.value()]
        )


class BaseHasRelatedFilter(admin.SimpleListFilter):
    """Базовый фильтр наличия связанных объектов."""

    related_field = None
    CHOICES_YES_NO = (
        ('yes', 'Да'),
        ('no', 'Нет'),
    )

    def lookups(self, request, model_admin):
        return self.CHOICES_YES_NO

    def queryset(self, request, objects):
        if not self.value():
            return objects
        condition = {
            f'{self.related_field}__isnull': self.value() == 'no'
        }

        return objects.filter(**condition).distinct()


class HasRecipesFilter(BaseHasRelatedFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    related_field = 'recipes'


class HasSubscriptionsFilter(BaseHasRelatedFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    related_field = 'subscriptions'


class HasSubscribersFilter(BaseHasRelatedFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'
    related_field = 'author_subscriptions'


class HasInRecipesFilter(BaseHasRelatedFilter):
    title = 'Есть в рецептах'
    parameter_name = 'has_in_recipes'
    related_field = 'recipe_ingredients'
