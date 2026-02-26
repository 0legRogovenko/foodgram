import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import recipes.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=128,
                        verbose_name='Название ингредиента'
                    ),
                ),
                (
                    'measurement_unit',
                    models.CharField(
                        max_length=64,
                        verbose_name='Единица измерения'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['name'],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('name', 'measurement_unit'),
                        name='unique_name_measurement_unit'
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=32,
                        unique=True,
                        verbose_name='Название тега'
                    ),
                ),
                (
                    'slug',
                    models.SlugField(
                        max_length=32,
                        unique=True,
                        verbose_name='URL-идентификатор тега'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name='last login'
                    ),
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'Designates that this user has all permissions '
                            'without explicitly assigning them.'
                        ),
                        verbose_name='superuser status',
                    ),
                ),
                (
                    'first_name',
                    models.CharField(max_length=150, verbose_name='Имя'),
                ),
                (
                    'last_name',
                    models.CharField(max_length=150, verbose_name='Фамилия'),
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'Designates whether the user can log into this admin site.'
                        ),
                        verbose_name='staff status',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text=(
                            'Designates whether this user should be treated as active. '
                            'Unselect this instead of deleting accounts.'
                        ),
                        verbose_name='active',
                    ),
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='date joined'
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        max_length=254,
                        unique=True,
                        verbose_name='Электронная почта'
                    ),
                ),
                (
                    'username',
                    models.CharField(
                        error_messages={
                            'unique': 'A user with that username already exists.',
                        },
                        help_text=(
                            'Required. 150 characters or fewer. Letters, digits and '
                            '@/./+/-/_ only.'
                        ),
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name='Имя пользователя',
                    ),
                ),
                (
                    'avatar',
                    models.ImageField(
                        blank=True,
                        max_length=255,
                        null=True,
                        upload_to='avatars/',
                        verbose_name='Аватар'
                    ),
                ),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            'The groups this user belongs to. A user will get all '
                            'permissions granted to each of their groups.'
                        ),
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.group',
                        verbose_name='groups',
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True,
                        help_text='Specific permissions for this user.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.permission',
                        verbose_name='user permissions',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=256, verbose_name='Название рецепта'),
                ),
                (
                    'image',
                    models.ImageField(
                        upload_to='recipes/',
                        verbose_name='Изображение блюда'
                    ),
                ),
                (
                    'text',
                    models.TextField(verbose_name='Описание приготовления'),
                ),
                (
                    'cooking_time',
                    models.PositiveIntegerField(
                        help_text='Время приготовления в минутах',
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name='Время приготовления (мин)',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Дата создания рецепта'
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='recipes',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Автор рецепта',
                    ),
                ),
                (
                    'ingredients',
                    models.ManyToManyField(
                        related_name='recipes',
                        through='recipes.RecipeIngredient',
                        to='recipes.ingredient',
                        verbose_name='Ингредиенты',
                    ),
                ),
                (
                    'tags',
                    models.ManyToManyField(
                        related_name='recipes',
                        to='recipes.tag',
                        verbose_name='Теги',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subscribers',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Автор',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subscriptions',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Подписчик',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'constraints': [
                    models.UniqueConstraint(
                        fields=('user', 'author'),
                        name='unique_subscription'
                    ),
                    models.CheckConstraint(
                        condition=~models.Q(user=models.F('author')),
                        name='prevent_self_subscription'
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='recipes.recipe',
                        verbose_name='Рецепт'
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Пользователь'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины покупок',
                'constraints': [
                    models.UniqueConstraint(
                        fields=('user', 'recipe'),
                        name='unique_shopping_cart'
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'amount',
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name='Количество'
                    ),
                ),
                (
                    'ingredient',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='ingredient_in_recipes',
                        to='recipes.ingredient',
                        verbose_name='Ингредиент',
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='recipe_ingredients',
                        to='recipes.recipe',
                        verbose_name='Рецепт',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Ингредиент рецепта',
                'verbose_name_plural': 'Ингредиенты рецепта',
                'constraints': [
                    models.UniqueConstraint(
                        fields=('recipe', 'ingredient'),
                        name='unique_recipe_ingredient'
                    ),
                    models.CheckConstraint(
                        condition=models.Q(amount__gt=0),
                        name='positive_amount'
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='recipes.recipe',
                        verbose_name='Рецепт'
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Пользователь'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные рецепты',
                'constraints': [
                    models.UniqueConstraint(
                        fields=('user', 'recipe'),
                        name='unique_favorite'
                    )
                ],
            },
        ),
    ]
