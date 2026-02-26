from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .constants import MIN_AMOUNT, MIN_COOKING_TIME


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        max_length=255,
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        """
        Возвращает строковое представление пользователя.

        Returns:
            str: username пользователя.
        """
        return self.username

    def get_full_name(self):
        """
        Возвращает полное имя пользователя.

        Returns:
            str: строка вида 'Имя Фамилия'.
        """
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    """Модель подписки пользователя на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    def __str__(self):
        """
        Возвращает строковое представление подписки.

        Returns:
            str: строка вида 'user подписался на author'.
        """
        return f'{self.user} подписался на {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Tag(models.Model):
    """Тег, используемый для классификации рецептов."""
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Название тега',
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name='URL-идентификатор тега'
    )

    def __str__(self):
        """Возвращает название тега."""
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Ингредиент, используемый в рецептах."""

    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        """Возвращает название ингредиента."""
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'name', 'measurement_unit'
                ],
                name='unique_name_measurement_unit'),
        ]
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Рецепт, созданный пользователем."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение блюда'
    )
    text = models.TextField(
        verbose_name='Описание приготовления'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME)],
        verbose_name='Время приготовления (мин)',
        help_text='Время приготовления в минутах'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта'
    )

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """Промежуточная модель между Recipe и Ingredient."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Количество'
    )

    def __str__(self):
        """Возвращает строку вида 'Ингредиент — количество единиц'."""
        return (f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}'
                )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='positive_amount'
            )
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class UserRecipeBase(models.Model):
    """Базовая модель для связи User с Recipe (избранное, корзина)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class Favorite(UserRecipeBase):
    """Модель избранных рецептов пользователя."""

    def __str__(self):
        """Возвращает строку вида 'user добавил recipe в избранное'."""
        return f'{self.user} добавил {self.recipe} в избранное'

    class Meta(UserRecipeBase.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(UserRecipeBase):
    """Модель корзины покупок пользователя."""

    def __str__(self):
        """Возвращает строку вида 'user добавил recipe в корзину'."""
        return f'{self.user} добавил {self.recipe} в корзину'

    class Meta(UserRecipeBase.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
