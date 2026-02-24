import json

from api.models import Ingredient
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


class Command(BaseCommand):
    """
    Management команда для загрузки ингредиентов из JSON файла.

    Загружает список ингредиентов в базу данных и выводит
    статистику загрузки.
    """

    help = 'Загружает ингредиенты из JSON файла в БД'

    def add_arguments(self, parser):
        """
        Добавляет параметры командной строки.

        Args:
            parser: ArgumentParser объект.
        """
        parser.add_argument(
            '--file',
            type=str,
            default='data/ingredients.json',
            help='Путь к JSON файлу с ингредиентами',
        )

    def handle(self, *args, **options):
        """
        Основная логика команды загрузки ингредиентов.

        Args:
            *args: Позиционные аргументы команды.
            **options: Именованные аргументы команды.
        """
        file_path = options['file']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ingredients = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
            return
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(f'Ошибка чтения JSON из {file_path}')
            )
            return

        created_count = 0
        skipped_count = 0

        for ingredient_data in ingredients:
            try:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_data['name'],
                    measurement_unit=ingredient_data['measurement_unit'],
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1
            except (KeyError, IntegrityError) as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Ошибка при загрузке: {ingredient_data}. {str(e)}'
                    )
                )
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Загружено ингредиентов: {created_count}\n'
                f'✓ Пропущено (уже существуют): {skipped_count}\n'
                f'✓ Всего ингредиентов в БД: {Ingredient.objects.count()}'
            )
        )
