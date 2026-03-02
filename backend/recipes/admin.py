from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .filters import (CookingTimeFilter, HasInRecipesFilter, HasRecipesFilter,
                      HasSubscribersFilter, HasSubscriptionsFilter)
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag, User)


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


class RecipesCountMixin:
    list_display = ['recipes_count']

    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Страничка управления тегами в админке."""

    list_display = [*RecipesCountMixin.list_display, 'id', 'name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['name']


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Страничка управления продуктами в админке."""

    list_display = [*RecipesCountMixin.list_display,
                    'id', 'name', 'measurement_unit']
    list_filter = ['measurement_unit', HasInRecipesFilter]
    search_fields = ['name', 'measurement_unit']
    ordering = ['name', 'measurement_unit']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Страничка управления рецептами в админке."""

    list_display = [
        'id', 'display_name', 'display_author', 'display_cooking_time',
        'display_image', 'display_products', 'display_tags', 'favorites_count'
    ]
    list_filter = ['author', 'tags', CookingTimeFilter]
    search_fields = ['name', 'author__username', 'tags__name',
                     'ingredients__name']
    ordering = ['name']
    readonly_fields = ['display_image', 'favorites_count']
    filter_horizontal = ['tags']
    inlines = []
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'author',
                    'text',
                    'cooking_time',
                    'tags',
                    ('image', 'display_image'),
                    'favorites_count',
                )
            },
        ),
    )

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
    def display_products(self, recipe):
        """Показать список продуктов."""
        return mark_safe(
            '<br>'.join(
                (
                    f'{item.ingredient.name} '
                    f'({item.amount} {item.ingredient.measurement_unit})'
                )
                for item in recipe.recipe_ingredients.select_related(
                    'ingredient'
                ).all()
            )
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        """Показать список тегов."""
        return mark_safe('<br>'.join(tag.name for tag in obj.tags.all()))

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        """Количество добавлений рецепта в избранное."""
        return recipe.favorite.count()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ['ingredient', 'amount']


RecipeAdmin.inlines = [RecipeIngredientInline]


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


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeBaseAdmin):
    """Страничка управления списком покупок в админке."""


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Страничка управления подписками в админке."""

    list_display = ['id', 'user', 'author']
    search_fields = ['user__username', 'author__username']
    ordering = ['user']


@admin.register(User)
class UserAdmin(BaseUserAdmin, RecipesCountMixin):
    """Страничка управления пользователями в админке."""

    list_display = [*RecipesCountMixin.list_display, 'id',
                    'username', 'full_name',
                    'email', 'display_avatar',
                    'subscriptions_count',
                    'subscribers_count'
                    ]
    list_filter = ['is_staff', 'is_superuser', HasRecipesFilter,
                   HasSubscriptionsFilter, HasSubscribersFilter]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {
                'fields': (
                    'first_name', 'last_name', 'email', 'avatar',
                    'display_avatar'
                )
            },
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
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
        return user.get_full_name()

    @admin.display(description='Аватар')
    def display_avatar(self, user):
        """Показать аватар пользователя."""
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}" width="50" height="50" '
                'style="border-radius: 50%; object-fit: cover;" />'
            )
        return '-'

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        """Количество подписок пользователя."""
        return user.subscriptions.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        """Количество подписчиков пользователя."""
        return user.author_subscriptions.count()
