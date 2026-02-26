from recipes.models import Ingredient
from .base import BaseImportCommand


class Command(BaseImportCommand):
    """
    Management команда для загрузки ингредиентов из JSON файла.

    Загружает список ингредиентов в базу данных и выводит
    статистику загрузки.
    """

    model = Ingredient
    default_file_path = 'data/ingredients.json'
    help = 'Загружает ингредиенты из JSON файла в БД'
