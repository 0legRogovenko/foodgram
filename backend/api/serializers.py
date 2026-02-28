from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField as DRFBase64ImageField
from recipes.constants import MIN_AMOUNT, MIN_COOKING_TIME
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Subscription,
                            Tag, User)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UsersBaseSerializer(UserSerializer):
    """Миксин для сериализаторов пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, user):
        """
        Проверяет, подписан ли текущий пользователь на данного пользователя.
        """
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Subscription.objects.filter(
                    user=request.user,
                    author=user).exists()
                )

    class Meta(UserSerializer.Meta):
        fields = [*UserSerializer.Meta.fields, 'is_subscribed']
        read_only_fields = UserSerializer.Meta.fields


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = fields


class UserWithRecipesSerializer(UsersBaseSerializer):
    """Сериализатор пользователя с его рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    def get_recipes(self, user):
        """Метод для получения рецептов"""
        request = self.context.get('request')
        recipes = user.recipes.all()
        raw_limit = request.query_params.get(
            'recipes_limit',
            10 ** 10
        )
        try:
            recipes_limit = int(raw_limit)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                {'recipes_limit': 'Укажите целое число.'}) from exc
        if recipes_limit < 1:
            raise ValidationError(
                {'recipes_limit': 'Значение должно быть больше нуля.'})

        return ShortRecipeSerializer(
            recipes[:recipes_limit],
            many=True
        ).data

    class Meta(UsersBaseSerializer.Meta):
        fields = [*UsersBaseSerializer.Meta.fields, 'recipes', 'recipes_count']
        read_only_fields = fields


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для получения аватара пользователя."""
    avatar = DRFBase64ImageField(required=False)

    class Meta:
        model = User
        fields = ['avatar']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = fields


class IngredientAmountCreateSerializer(serializers.Serializer):
    """Сериализатор для создания ингредиента с количеством."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT,
        required=True
    )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели Recipe."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def _check_user_relation(self, obj, related_name):
        """Проверяет связь пользователя с объектом."""
        request = self.context.get('request')
        if not (request and request.user.is_authenticated):
            return False
        return getattr(obj, related_name).filter(user=request.user).exists()


    def get_is_favorited(self, obj):
        """Проверяет, добавил ли пользователь рецепт в избранное."""
        return self._check_user_relation(obj, 'favorite_set')

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в корзине пользователя."""
        return self._check_user_relation(obj, 'shoppingcart_set')

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]
        read_only_fields = fields


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления модели Recipe."""

    image = DRFBase64ImageField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    ingredients = IngredientAmountCreateSerializer(
        source='recipe_ingredients',
        many=True,
        required=True,
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        ]
        read_only_fields = ['id', 'author']

    def _create_ingredients(self, recipe, ingredients_data):
        """Метод для создания ингредиентов рецепта."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        )

    def _set_tags(self, recipe, tags):
        """Метод для установки тегов рецепта."""
        recipe.tags.set(tags)

    def validate(self, attrs):
        ingredient_data = attrs.get('recipe_ingredients')
        tags = attrs.get('tags')

        if ingredient_data is not None:
            if not ingredient_data:
                raise ValidationError(
                    'Рецепт должен содержать хотя бы один ингредиент.'
                )

            ids = [item['id'].id for item in ingredient_data]
            if len(ids) != len(set(ids)):
                duplicates = [i for i in set(ids) if ids.count(i) > 1]
                raise ValidationError(
                    f'Ингредиенты должны быть уникальными. '
                    f'Повторяющиеся ингредиенты: '
                    f'{duplicates}'
                )

        if tags is not None:
            if not tags:
                raise ValidationError(
                    'Рецепт должен содержать хотя бы один тег.'
                )

            tag_ids = [t.id for t in tags]
            if len(tag_ids) != len(set(tag_ids)):
                duplicates = [t for t in set(tag_ids) if tag_ids.count(t) > 1]
                raise ValidationError(
                    f'Теги должны быть уникальными. '
                    f'Повторяющиеся теги: '
                    f'{duplicates}'
                )

        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        validated_data['author'] = self.context['request'].user

        recipe = super().create(validated_data)
        self._set_tags(recipe, tags)
        self._create_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredient_data = validated_data.pop('recipe_ingredients', None)

        self._set_tags(instance, tags)

        instance.recipe_ingredients.all().delete()
        self._create_ingredients(instance, ingredient_data)

        return super().update(instance, validated_data)
