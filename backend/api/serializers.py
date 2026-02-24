import base64
import re

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (Ingredient, Recipe, RecipeIngredient, Subscription, Tag,
                     User)


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""

    def to_internal_value(self, data):
        """Метод преобразования картинки"""

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class UsersMixinSerializer(serializers.ModelSerializer):
    """Миксин для сериализаторов пользователей."""

    id = serializers.IntegerField(
        read_only=True
    )
    email = serializers.EmailField(
        read_only=True
    )
    username = serializers.CharField(
        required=True,
        max_length=150
    )
    first_name = serializers.CharField(
        required=True,
        max_length=150
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150
    )
    avatar = serializers.ImageField(read_only=True, required=False)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного пользователя.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class UserSerializer(
    UsersMixinSerializer,
    serializers.ModelSerializer
):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    id = serializers.IntegerField(source='author.id', read_only=True)
    email = serializers.EmailField(source='author.email', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True)
    last_name = serializers.CharField(
        source='author.last_name', read_only=True)
    avatar = serializers.ImageField(
        source='author.avatar',
        read_only=True,
        required=False
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Подписано ли текущий пользователь на этого автора
        (всегда True, так как это подписка)
        """
        return True

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов автора."""

        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """Метод для получения рецептов"""

        request = self.context.get('request')
        recipes = obj.author.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    class Meta:
        model = Subscription
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed', 'recipes_count', 'recipes'
        ]


class UserCreateSerializer(
    UsersMixinSerializer,
    serializers.ModelSerializer
):
    """Сериализатор для создания пользователя."""

    id = serializers.IntegerField(
        read_only=True
    )
    avatar = serializers.ImageField(
        read_only=True,
        required=False
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )
    email = serializers.EmailField(
        required=True,
        max_length=254
    )
    password = serializers.CharField(
        write_only=True,
        required=True
    )

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

    def get_is_subscribed(self, obj):
        return False

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return value

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Недопустимые символы в username.'
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )
        return value

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя."""

    current_password = serializers.CharField(
        write_only=True,
        required=True
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate_current_password(self, value):
        """Проверяет правильность текущего пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value

    def validate_new_password(self, value):
        """Проверяет новый пароль на соответствие требованиям."""
        if len(value) < 8:
            raise serializers.ValidationError(
                'Новый пароль должен быть не менее 8 символов.'
            )
        return value

    def save(self, **kwargs):
        """Сохраняет новый пароль для пользователя."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для получения аватара пользователя."""
    avatar = Base64ImageField(
        required=False,
    )

    class Meta:
        model = User
        fields = ['avatar']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    id = serializers.IntegerField(
        read_only=True
    )
    name = serializers.CharField(
        required=True
    )
    slug = serializers.SlugField(
        required=True
    )

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    id = serializers.IntegerField(
        read_only=True
    )
    name = serializers.CharField(
        required=True
    )
    measurement_unit = serializers.CharField(
        required=True
    )

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'measurement_unit', 'amount', 'name']


class IngredientAmountSerializer(serializers.Serializer):
    """Сериализатор для отображения ингредиента с количеством."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)],
        required=True
    )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели Recipe."""

    id = serializers.IntegerField(
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = UserSerializer(
        read_only=True
    )
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        read_only=True
    )
    name = serializers.CharField(
        required=True
    )
    text = serializers.CharField(
        required=True
    )
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1)],
        required=True
    )

    def get_is_favorited(self, obj):
        """Проверяет, добавил ли пользователь рецепт в избранное."""

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в корзине пользователя."""

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.in_cart_by.filter(id=request.user.id).exists()
        return False

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания модели Recipe."""

    name = serializers.CharField(
        required=True
    )
    image = Base64ImageField(
        required=True
    )
    text = serializers.CharField(
        required=True
    )
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1)],
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    ingredients = IngredientAmountSerializer(
        source='recipe_ingredients',
        many=True,
        required=True,
    )

    def _create_ingredients(self, recipe, ingredients_data):
        """Метод для создания ингредиентов рецепта."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ])

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
                raise ValidationError('Ингредиенты должны быть уникальными.')

        if tags is not None:
            if not tags:
                raise ValidationError(
                    'Рецепт должен содержать хотя бы один тег.'
                )

            tag_ids = [t.id for t in tags]
            if len(tag_ids) != len(set(tag_ids)):
                raise ValidationError('Теги должны быть уникальными.')

        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')

        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        self._set_tags(recipe, tags)
        self._create_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredient_data = validated_data.pop('recipe_ingredients', None)

        if tags is not None:
            self._set_tags(instance, tags)

        if ingredient_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_ingredients(instance, ingredient_data)

        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'tags',
            'ingredients'
        ]
