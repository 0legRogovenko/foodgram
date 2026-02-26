from recipes.models import Tag

from .base import BaseImportCommand


class Command(BaseImportCommand):
    model = Tag
    default_file_path = 'data/tags.json'
    help = 'Загружает теги из JSON файла в БД'
