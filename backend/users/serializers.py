import djoser.serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from djoser.serializers import UserSerializer
# from api.serializers import Base64ImageField
from recipes.models import Subscribe, Favorite, ShoppingCart, Recipe

User = get_user_model()
# from users.models import User


class UsersSerializer(UserSerializer):
    """Создание пользователей."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
         )

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка на авторов."""
    id = serializers.IntegerField()

    class Meta:
        model = Subscribe
        fields = ('id', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class SubscriptionsSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    # recipes = RecipeSerializer()
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = Subscribe
        fields = ('id', 'author', 'recipes', 'recipes_count')

    def get_recipes_count(self, request, obj):
        pass


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
