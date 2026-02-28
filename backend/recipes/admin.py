from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from .filters import (CookingTimeFilter, HasInRecipesFilter, HasRecipesFilter,
                      HasSubscribersFilter, HasSubscriptionsFilter)
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag, User)


class BaseTagIngredientAdmin(admin.ModelAdmin):
    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        """Количество рецептов с этим тегом или продуктом"""
        return obj.recipes.count()


@admin.register(Tag)
class TagAdmin(BaseTagIngredientAdmin):
    """Страничка управления тегами в админке."""

    list_display = ['id', 'name', 'slug', 'recipes_count']
    search_fields = ['name', 'slug']
    ordering = ['name']


@admin.register(Ingredient)
class IngredientAdmin(BaseTagIngredientAdmin):
    """Страничка управления продуктами в админке."""

    list_display = ['id', 'name', 'measurement_unit', 'recipes_count']
    list_filter = ['measurement_unit', HasInRecipesFilter]
    search_fields = ['name', 'measurement_unit', 'recipes__name']
    ordering = ['name', 'measurement_unit']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Страничка управления рецептами в админке."""

    list_display = ['id', 'name', 'author', 'cooking_time', 'display_image',
                    'display_products', 'display_tags', 'favorites_count']
    list_filter = ['author', 'tags', CookingTimeFilter]
    search_fields = ['name', 'author__username', 'tags__name',
                     'recipe_ingredients__ingredient__name']
    ordering = ['name']
    readonly_fields = ['favorites_count']
    filter_horizontal = ['tags']

    @admin.display(description='Картинка')
    def display_image(self, recipe):
        """Показать картинку рецепта."""
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 4px;" />'
            )
        return '-'

    @admin.display(description='Продукты')
    def display_products(self, obj):
        """Показать список продуктов."""
        products = obj.recipe_ingredients.all()
        return mark_safe(
            '<br>'.join(
                (
                    f'{p.ingredient.name} '
                    f'({p.amount} {p.ingredient.measurement_unit})'
                )
                for p in products[:5]
            )
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        """Показать список тегов."""
        return format_html_join(
            '<br>',
            '{}',
            ((tag.name,) for tag in obj.tags.all())
        )

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorite_set.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Страничка управления рецептами связанными с продуктами в админке."""

    list_display = ['id', 'recipe', 'ingredient', 'amount']
    search_fields = ['recipe__name', 'ingredient__name']
    ordering = ['recipe']


class UserRecipeBaseAdmin(admin.ModelAdmin):
    """Базовый класс для избранного и списка покупок."""

    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    ordering = ['user']


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeBaseAdmin):
    """Страничка управления избранными рецептами в админке."""

    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeBaseAdmin):
    """Страничка управления списком покупок в админке."""

    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Страничка управления подписками в админке."""

    list_display = ['id', 'user', 'author']
    search_fields = ['user__username', 'author__username']
    ordering = ['user']


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseTagIngredientAdmin):
    """Страничка управления пользователями в админке."""

    list_display = ['id', 'username', 'full_name', 'email', 'display_avatar',
                    'recipes_count', 'subscriptions_count',
                    'subscribers_count'
                    ]
    list_filter = ['is_staff', 'is_superuser', HasRecipesFilter,
                   HasSubscriptionsFilter, HasSubscribersFilter]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {'fields': ('first_name', 'last_name', 'email', 'avatar')},
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                ),
            },
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ['display_avatar']

    @admin.display(description='ФИО')
    def full_name(self, user):
        """Полное имя пользователя."""
        full_name = user.get_full_name()
        return full_name

    @admin.display(description='Аватар')
    def display_avatar(self, obj):
        """Показать аватар пользователя."""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" '
                'style="border-radius: 50%; object-fit: cover;" />'
            )
        return '-'

    @admin.display(description='Подписок')
    def subscriptions_count(self, obj):
        """Количество подписок пользователя."""
        return obj.subscriptions.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, obj):
        """Количество подписчиков пользователя."""
        return obj.author_subscriptions.count()
