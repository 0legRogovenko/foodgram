"""Утилиты для приложения recipes."""
from datetime import datetime

from django.db.models import F, Sum
from django.template.loader import render_to_string

from .models import RecipeIngredient


def format_shopping_list(cart_items):
    """Форматирует список покупок на основе товаров в корзине."""

    # Получить все ингредиенты для рецептов в корзине одним запросом
    ingredients_data = RecipeIngredient.objects.filter(
        recipe__shoppingcart_set__in=cart_items
    ).values(
        ingredient_name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(
        total_amount=Sum('amount')
    ).distinct()

    # Дедублицировать и форматировать ингредиенты
    ingredients = {}
    for item in ingredients_data:
        key = item['ingredient_name'].lower()
        if key not in ingredients:
            ingredients[key] = {
                'name': item['ingredient_name'].capitalize(),
                'amount': item['total_amount'],
                'unit': item['measurement_unit'],
            }
        else:
            # Если уже есть - суммировать количество
            ingredients[key]['amount'] += item['total_amount']

    # Форматировать продукты с их единицами
    products = [
        f"{data['name']} – {data['amount']} {data['unit']}"
        for data in sorted(ingredients.values(), key=lambda x: x['name'])
    ]

    # Собрать список рецептов с авторами
    recipes = []
    seen = set()
    for item in cart_items:
        key = (item.recipe.name, item.recipe.author.username)
        if key not in seen:
            recipes.append(key)
            seen.add(key)

    context = {
        'created_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'products': products,
        'recipes': recipes,
    }

    return render_to_string('shopping_list.txt', context)
