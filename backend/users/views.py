import djoser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.permissions import IsAuthorOrReadOnly
from recipes.models import Recipe, Subscribe
from users.serializers import (
    UsersSerializer, SubscribeSerializer, SubscriptionsSerializer,
    # SubscriptionsSerializer
)

User = get_user_model()


class UsersViewSet(UserViewSet):
    """Операции с пользователями."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permissions_class = (IsAuthenticated,)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=request.data.get('id'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(data=serializer.validated_data)
        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user,
                              author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthorOrReadOnly,)
            )
    def subscriptions(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        serializer = SubscriptionsSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.get(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



