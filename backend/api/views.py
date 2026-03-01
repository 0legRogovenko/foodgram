from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag, User)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import LimitPageNumberPagination
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer, UserSerializer,
                          UserWithRecipesSerializer)
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

    def _toggle_relation(self, request, model_class):
        user = request.user
        recipe_id = self.kwargs['pk']

        exists = model_class.objects.filter(
            user=user,
            recipe_id=recipe_id
        ).exists()

        if request.method == 'DELETE':

            if not exists:
                raise ValidationError({'detail': 'Не найдено.'})

            model_class.objects.filter(
                user=user,
                recipe_id=recipe_id
            ).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        if exists:
            raise ValidationError({'detail': 'Уже добавлено.'})

        model_class.objects.create(
            user=user,
            recipe_id=recipe_id
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self._toggle_relation(
            request,
            Favorite,
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self._toggle_relation(
            request,
            ShoppingCart,

        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):

        return FileResponse(
            format_shopping_list(
                request.user.shoppingcart_set.all()), as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )

    @action(
        detail=True,
        methods=['get'])
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise ValidationError({'detail': f'Рецепт с id={pk} не найден.'})

        return Response({'short_link': request.build_absolute_uri(
            reverse('short-link', args=[pk])
        )})


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

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user

        if request.method == 'DELETE':
            get_object_or_404(
                Subscription,
                user=user,
                author_id=pk
            ).delete()
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

        return self.get_paginated_response(
            UserWithRecipesSerializer(
                [s.author for s in self.paginate_queryset(
                    request.user.subscriptions.all())],
                many=True,
                context={'request': request.user.subscriptions.all()}
            ).data
        )
