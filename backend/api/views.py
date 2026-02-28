from uuid import uuid4

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            ShortLink, Subscription, Tag, User)

from .filters import RecipeFilter
from .pagination import LimitPageNumberPagination
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShortRecipeSerializer,
                          TagSerializer, UserSerializer,
                          UserWithRecipesSerializer)
from .utils import format_shopping_list


def _generate_short_code(length=10):
    return uuid4().hex[:length]


def short_link_redirect(request, code):
    short_link = get_object_or_404(ShortLink, code=code)
    return redirect('recipes-detail', pk=short_link.recipe_id)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = LimitPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'tags', 'recipe_ingredients__ingredient'
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def _toggle_relation(self, request,
                         model_class, already_msg,
                         not_found_msg):
        user = request.user
        recipe = self.get_object()

        if request.method == 'DELETE':
            deleted, _ = model_class.objects.filter(
                user=user, recipe=recipe).delete()
            if not deleted:
                raise ValidationError(not_found_msg)
            return Response(status=status.HTTP_204_NO_CONTENT)

        _, created = model_class.objects.get_or_create(
            user=user, recipe=recipe)
        if not created:
            raise ValidationError(already_msg)

        return Response(
            ShortRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self._toggle_relation(
            request,
            Favorite,
            already_msg='Рецепт уже добавлен в избранное.',
            not_found_msg='Этого рецепта нет в избранном.'
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self._toggle_relation(
            request,
            ShoppingCart,
            already_msg='Рецепт уже в списке покупок.',
            not_found_msg='Этого рецепта нет в списке покупок.'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart_items = request.user.shoppingcart_set.all()
        content = format_shopping_list(cart_items)

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = ShortLink.objects.filter(recipe=recipe).first()
        if short_link is None:
            code = _generate_short_code()
            while ShortLink.objects.filter(code=code).exists():
                code = _generate_short_code()
            short_link = ShortLink.objects.create(recipe=recipe, code=code)
        short_url = request.build_absolute_uri(
            reverse('short-link', args=[short_link.code])
        )

        return Response({'short-link': short_url})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    def patch(self, request, *args, **kwargs):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user

        if request.method == 'DELETE':
            deleted, _ = Subscription.objects.filter(
                user=user,
                author_id=pk
            ).delete()
            if not deleted:
                raise ValidationError('Вы не были подписаны на этого автора.')
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = self.get_object()

        if user == author:
            raise ValidationError('Нельзя подписаться на себя')

        _, created = Subscription.objects.get_or_create(
            user=user,
            author=author
        )
        if not created:
            raise ValidationError(
                f'Вы уже подписаны на @{author.username}'
            )

        return Response(
            UserWithRecipesSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = request.user.subscriptions.all()
        page = self.paginate_queryset(subscriptions)

        return self.get_paginated_response(
            UserWithRecipesSerializer(
                [s.author for s in page],
                many=True,
                context={'request': request}
            ).data
        )
