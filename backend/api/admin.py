from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag, User)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Страничка управления тегами в админке."""

    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['name', ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Страничка управления ингредиаентами в админке."""

    list_display = ['name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    ordering = ['name', ]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Страничка управления рецептами в админке."""

    list_display = [
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'created_at',
        'favorites_count',
    ]
    search_fields = [
        'author__username',
        'name',
        'text',
        'created_at'
    ]
    ordering = ['name', ]
    readonly_fields = ['favorites_count']
    filter_horizontal = ['tags']
    list_filter = ['tags', 'created_at']

    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorited_by.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """
    Страничка управления рецептами связанными с ингредиентами в админке.
    """

    list_display = [
        'recipe',
        'ingredient',
        'amount',
    ]
    search_fields = ['recipe', 'ingredient']
    ordering = ['recipe']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Страничка управления избранными рецептами в админке."""

    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    ordering = ['user']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Страничка управления списком покупок в админке."""

    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    ordering = ['user']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Страничка управления подписками в админке."""

    list_display = ['user', 'author']
    search_fields = ['user__username', 'author__username']
    ordering = ['user']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {'fields': ('first_name', 'last_name', 'email')},
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
    search_fields = ('username', 'email')
    ordering = ('username',)
