from datetime import datetime

from django.db.models import F, Sum
from django.template.loader import render_to_string

from recipes.models import RecipeIngredient


def format_shopping_list(cart_items):
    """Форматирует список покупок на основе товаров в корзине."""

    ingredients_data = RecipeIngredient.objects.filter(
        recipe__shoppingcart_set__in=cart_items
    ).values(
        ingredient_name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(
        total_amount=Sum('amount')
    ).distinct()

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
            ingredients[key]['amount'] += item['total_amount']

    products = products = sorted(ingredients.values(), key=lambda x: x['name'])

    recipes = (
        cart_items
        .values_list('recipe__name', 'recipe__author__username')
        .distinct()
    )

    context = {
        'created_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'products': products,
        'recipes': recipes,
    }

    return render_to_string('shopping_list.txt', context)
