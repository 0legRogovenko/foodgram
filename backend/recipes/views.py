from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Ingredient, Recipe, Subscription, Tag, User
from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    ShortRecipeSerializer, TagSerializer, UserSerializer,
    UserWithRecipesSerializer
)
from .utils import format_shopping_list


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

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_link']:
            return [AllowAny()]
        if self.action in [
            'create', 'favorite', 'shopping_cart', 'download_shopping_cart'
        ]:
            return [IsAuthenticated()]
        if self.action in ['partial_update', 'destroy']:
            return [IsAuthorOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        user = request.user

        if request.method == 'POST':
            recipe = self.get_object()
            _, created = user.favorite_set.get_or_create(recipe=recipe)
            if not created:
                raise ValidationError('Рецепт уже в избранном')
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(user.favorite_set, recipe__pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        user = request.user

        if request.method == 'POST':
            recipe = self.get_object()
            _, created = user.shoppingcart_set.get_or_create(recipe=recipe)
            if not created:
                raise ValidationError('Рецепт уже в списке покупок')
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(user.shoppingcart_set, recipe__pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        cart_items = request.user.shoppingcart_set.all()
        if not cart_items.exists():
            raise ValidationError('Корзина пуста')

        shopping_list = format_shopping_list(cart_items)
        return FileResponse(
            shopping_list,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        short_link = request.build_absolute_uri(
            reverse('recipes-detail', args=[pk]))
        return Response({'short-link': short_link})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']
    http_method_names = ['get']


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = self.get_object()

        if request.method == 'POST':
            if user == author:
                raise ValidationError('Нельзя подписаться на себя')

            subscription, created = Subscription.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                raise ValidationError(
                    f'Вы уже подписаны на @{author.username}')

            return Response(
                UserWithRecipesSerializer(
                    author, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(Subscription, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)

        if page is not None:
            return self.get_paginated_response(
                UserWithRecipesSerializer(
                    [s.author for s in page],
                    many=True,
                    context={'request': request}
                ).data
            )

        return Response(
            UserWithRecipesSerializer(
                [s.author for s in subscriptions],
                many=True,
                context={'request': request}
            ).data
        )
