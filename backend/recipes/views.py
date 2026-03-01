from django.shortcuts import redirect
from recipes.models import Recipe


def short_link_redirect(request, recipe_id):
    if not Recipe.objects.filter(pk=recipe_id).exists():
        return redirect('/404/')

    return redirect(f'/api/recipes/{recipe_id}/')
