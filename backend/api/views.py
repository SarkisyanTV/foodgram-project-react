from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, AllowAny
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from foodgram.settings import UPLOAD_NAME
from recipes.models import (
    Ingredient, Tag, Recipe, RecipeIngredient,
    ShoppingCart, Favorite, Subscribe
)
from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeIngredientSerializer, RecipeCreateSerializer,
    UsersSerializer, SubscribeSerializer,
    SubscriptionsSerializer, RecipeSubscribeSerializer
)

User = get_user_model()


class UsersViewSet(UserViewSet):
    """Операции с пользователями."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permissions_class = (IsAuthenticated,)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        subscribe_queryset = get_list_or_404(
            User,
            subscribe_author__user=request.user
        )
        users_obj = self.paginate_queryset(subscribe_queryset)
        serializer = SubscriptionsSerializer(
            users_obj, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=kwargs['id'])

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user,
                              author=author).delete()
            return Response({'errors': 'Вы отписаны от этого автора.'},
                            status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeIngredientViewSet(ModelViewSet):

    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(ModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            serializer = RecipeSubscribeSerializer(
                recipe, data=request.data, context={'request':request}
            )
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'error': 'Рецепт уже добавлен в избранное.'})
        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSubscribeSerializer(
                recipe, data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'ingredient__measurement_unit',
                         'total_amount',
                         )
        )
        shopping_list = []
        [shopping_list.append(
            '* {} - ({}) {}'.format(*ingredient)) for ingredient in ingredients]
        upload_file = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(shopping_list),
            content_type='text/plain'
        )
        upload_file['Content-Disposition'] = f'attachment; filename={UPLOAD_NAME}'
        return upload_file
