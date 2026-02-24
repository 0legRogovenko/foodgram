from django.contrib.auth import get_user_model

from api.models import Ingredient, Recipe, RecipeIngredient, Tag

from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    """
    Management команда для создания тестовых данных.

    Создает тестовых пользователей, теги и рецепты в базе данных
    для облегчения тестирования API.
    """

    help = 'Загружает тестовых пользователей и рецепты'

    def handle(self, *args, **options):
        """
        Основная логика команды загрузки тестовых данных.

        Args:
            *args: Позиционные аргументы команды.
            **options: Именованные аргументы команды.
        """

        users_data = [
            {
                'email': 'admin@example.com',
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': 'admin12345',
            },
            {
                'email': 'chef@example.com',
                'username': 'chef',
                'first_name': 'Chef',
                'last_name': 'Master',
                'password': 'chef12345',
            },
            {
                'email': 'user@example.com',
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'test12345',
            },
        ]

        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                },
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                created_users.append(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Пользователь "{user.username}" создан'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Пользователь "{user.username}" уже существует'
                    )
                )

        tags_data = [
            {'name': 'Завтрак', 'slug': 'breakfast'},
            {'name': 'Обед', 'slug': 'lunch'},
            {'name': 'Ужин', 'slug': 'dinner'},
        ]

        created_tags = []
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={
                    'slug': tag_data['slug'],
                },
            )
            if created:
                created_tags.append(tag)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Тег "{tag.name}" создан')
                )

        if created_users:
            author = created_users[0]
        else:
            author = User.objects.first()

        ingredients = Ingredient.objects.all()[:10]
        if not ingredients.exists():
            self.stdout.write(
                self.style.WARNING(
                    '⚠ Нет ингредиентов в БД. '
                    'Сначала загрузите ингредиенты.'
                )
            )
            return

        recipes_data = [
            {
                'name': 'Паста Карбонара',
                'text': (
                    'Классическая итальянская паста с беконом, '
                    'яйцами и пармезаном'
                ),
                'cooking_time': 25,
                'ingredients': [ingredients[0]],
                'tags': [created_tags[0]] if created_tags else [],
            },
            {
                'name': 'Омлет с беконом',
                'text': 'Быстрый омлет для завтрака с хрустящим беконом',
                'cooking_time': 10,
                'ingredients': (
                    [ingredients[1], ingredients[2]]
                    if len(ingredients) > 2
                    else ingredients[:2]
                ),
                'tags': [created_tags[0]] if created_tags else [],
            },
            {
                'name': 'Салат Цезарь',
                'text': (
                    'Классический салат с курицей, сухариками '
                    'и соусом Цезарь'
                ),
                'cooking_time': 15,
                'ingredients': (
                    [ingredients[3], ingredients[4]]
                    if len(ingredients) > 4
                    else ingredients[3:]
                ),
                'tags': [created_tags[1]] if created_tags else [],
            },
        ]

        for recipe_data in recipes_data:
            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data['name'],
                author=author,
                defaults={
                    'text': recipe_data['text'],
                    'cooking_time': recipe_data['cooking_time'],
                },
            )

            if created:

                recipe.tags.set(recipe_data['tags'])

                for ingredient in recipe_data['ingredients']:
                    RecipeIngredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ingredient,
                        defaults={'amount': 100},
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Рецепт "{recipe.name}" создан'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Рецепт "{recipe.name}" уже существует'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Тестовые данные загружены!')
        )
