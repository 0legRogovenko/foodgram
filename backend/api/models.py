from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    """
    Тег, используемый для классификации рецептов.

    Атрибуты:
        name (str): название тега.
        slug (str): уникальный URL-идентификатор тега.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        """Возвращает название тега."""
        return self.name


class Ingredient(models.Model):
    """
    Ингредиент, используемый в рецептах.

    Атрибуты:
        name (str): название ингредиента.
        measurement_unit (str): единица измерения (г, мл, шт и т.д.).
    """
    name = models.CharField(max_length=100, db_index=True)
    measurement_unit = models.CharField(max_length=30)

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


class Recipe(models.Model):
    """
    Рецепт, созданный пользователем.

    Атрибуты:
        author (User): автор рецепта.
        name (str): название рецепта.
        image (Image): изображение блюда.
        text (str): описание приготовления.
        cooking_time (int): время приготовления в минутах.
        tags (Tag): теги рецепта.
        ingredients (Ingredient): ингредиенты через промежуточную модель.
        created_at (datetime): дата создания рецепта.
    """
    author = models.ForeignKey(
        'api.User', on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)],
        help_text='Время приготовления в минутах'
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name

    def favorites_count(self):
        """
        Возвращает количество пользователей,
        добавивших рецепт в избранное.

        Returns:
            int: число добавлений в избранное.
        """
        return self.favorited_by.count()

    def is_favorited_by(self, user):
        """
        Проверяет, добавил ли пользователь рецепт в избранное.

        Args:
            user (User): пользователь.

        Returns:
            bool: True, если рецепт в избранном.
        """
        return self.favorited_by.filter(id=user.id).exists()

    def is_in_cart(self, user):
        """
        Проверяет, находится ли рецепт в корзине пользователя.

        Args:
            user (User): пользователь.

        Returns:
            bool: True, если рецепт в корзине.
        """
        return self.in_cart_by.filter(id=user.id).exists()

    class Meta:
        ordering = ['-created_at']


class RecipeIngredient(models.Model):
    """
    Промежуточная модель между Recipe и Ingredient.

    Атрибуты:
        recipe (Recipe): рецепт.
        ingredient (Ingredient): ингредиент.
        amount (Decimal): количество ингредиента.

    Ограничения:
        - уникальная пара (recipe, ingredient)
        - amount > 0
    """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
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
                check=models.Q(amount__gt=0), name='positive_amount')
        ]


class Favorite(models.Model):
    """
    Модель избранных рецептов пользователя.

    Атрибуты:
        user (User): пользователь.
        recipe (Recipe): рецепт.

    Ограничения:
        - уникальная пара (user, recipe)
    """
    user = models.ForeignKey(
        'api.User', on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    def __str__(self):
        """Возвращает строку вида 'user добавил recipe в избранное'."""
        return f'{self.user} добавил {self.recipe} в избранное'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]


class ShoppingCart(models.Model):
    """
    Модель корзины покупок пользователя.

    Атрибуты:
        user (User): пользователь.
        recipe (Recipe): рецепт.

    Ограничения:
        - уникальная пара (user, recipe)
    """
    user = models.ForeignKey(
        'api.User', on_delete=models.CASCADE, related_name='cart_items')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_cart_by')

    def __str__(self):
        """Возвращает строку вида 'user добавил recipe в корзину'."""
        return f'{self.user} добавил {self.recipe} в корзину'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart_item')
        ]


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Наследует стандартную модель Django `AbstractUser`, добавляя:
    - уникальный email
    - аватар пользователя
    - корректные ограничения на длину имени и фамилии

    Используется для регистрации, авторизации и связи с рецептами.
    """
    email = models.EmailField(unique=True, )
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(
        max_length=255, upload_to='avatars/', blank=True, null=True)

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
            str: строка вида "Имя Фамилия".
        """
        return f"{self.first_name} {self.last_name}"

    def recipes_count(self):
        """
        Возвращает количество рецептов, созданных пользователем.

        Returns:
            int: число рецептов.
        """
        return self.recipes.count()


class Subscription(models.Model):
    """
    Модель подписки пользователя на автора.

    Атрибуты:
        user (User): пользователь, который подписывается.
        author (User): автор, на которого оформлена подписка.

    Ограничения:
        - пользователь не может подписаться сам на себя
        - пара (user, author) должна быть уникальной
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers')

    def __str__(self):
        """
        Возвращает строковое представление подписки.

        Returns:
            str: строка вида "user подписался на author".
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
