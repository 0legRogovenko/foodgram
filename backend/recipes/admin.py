from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .filters import (CookingTimeFilter, HasInRecipesFilter, HasRecipesFilter,
                      HasSubscribersFilter, HasSubscriptionsFilter)
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag, User)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Страничка управления тегами в админке."""

    list_display = ['id', 'name', 'slug', 'recipes_count']
    search_fields = ['name', 'slug']
    ordering = ['name']

    def recipes_count(self, obj):
        """Количество рецептов с этим тегом."""
        return obj.recipes.count()

    recipes_count.short_description = 'Рецептов'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Страничка управления продуктами в админке."""

    list_display = ['id', 'name', 'measurement_unit', 'recipes_count']
    list_filter = ['measurement_unit', HasInRecipesFilter]
    search_fields = ['name', 'measurement_unit', 'recipes__name']
    ordering = ['name', 'measurement_unit']

    def recipes_count(self, obj):
        """Количество рецептов с этим продуктом."""
        return obj.recipes.count()

    recipes_count.short_description = 'Рецептов'


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

    def display_image(self, obj):
        """Показать картинку рецепта."""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'

    display_image.short_description = 'Картинка'

    def display_products(self, obj):
        """Показать список продуктов."""
        products = obj.recipe_ingredients.all()
        if not products.exists():
            return '-'
        return format_html(
            '<br>'.join(
                (
                    f'{p.ingredient.name} '
                    f'({p.amount} {p.ingredient.measurement_unit})'
                )
                for p in products[:5]
            ) + ('<br>...' if products.count() > 5 else '')
        )

    display_products.short_description = 'Продукты'

    def display_tags(self, obj):
        """Показать список тегов."""
        tags = obj.tags.all()
        if not tags.exists():
            return '-'
        tag_strings = [f'<span>{tag.name}</span>' for tag in tags]
        return format_html(''.join(tag_strings))

    display_tags.short_description = 'Теги'

    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorite_set.count()

    favorites_count.short_description = 'В избранном'


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
class UserAdmin(BaseUserAdmin):
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

    def full_name(self, obj):
        """Полное имя пользователя."""
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else '-'

    full_name.short_description = 'ФИО'

    def display_avatar(self, obj):
        """Показать аватар пользователя."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return '-'

    display_avatar.short_description = 'Аватар'

    def recipes_count(self, obj):
        """Количество рецептов пользователя."""
        return obj.recipes.count()

    recipes_count.short_description = 'Рецептов'

    def subscriptions_count(self, obj):
        """Количество подписок пользователя."""
        return obj.subscriptions.count()

    subscriptions_count.short_description = 'Подписок'

    def subscribers_count(self, obj):
        """Количество подписчиков пользователя."""
        return obj.subscribers.count()

    subscribers_count.short_description = 'Подписчиков'
