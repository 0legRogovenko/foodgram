import json

from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    """Базовый класс для импорта JSON данных в БД."""

    model = None
    default_file_path = None
    help = None

    def add_arguments(self, parser):
        """Общая логика для всех команд."""
        parser.add_argument(
            '--file',
            type=str,
            default=self.default_file_path,
            help='Путь к JSON файлу'
        )

    def handle(self, *args, **options):
        """Общая логика загрузки."""
        try:
            with open(options['file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
            return

        objects = (self.model(**item) for item in data)
        created = self.model.objects.bulk_create(
            objects,
            ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загружено: {len(created)}\n'
                f'Всего в БД: {self.model.objects.count()}'
            )
        )
