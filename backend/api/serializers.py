import base64

import webcolors
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


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
            return obj.subscribe_author.filter(
                user=self.context['request'].user,
                author=obj).exists()
        return False


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка на авторов."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSubscribeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, obj):
        if self.context['request'].user == obj:
            raise serializers.ValidationError({'errors': 'Вы уже подписаны.'})
        return obj

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and obj.subscribe_author.filter(user=self.context['request'].user,
                                            author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Список авторов на которых подписан пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return (
            obj.subscribe_author.filter(user=self.context['request'].user,
                                        author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSubscribeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Покупки."""
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Получение тегов."""
    color = Hex2NameColor

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Получение ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Список ингредиентов с количеством для рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиенты для создания рецепта."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(
                'Количество не может быть меньше или равно 0.'
            )
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    """Получение рецептов при GET запросе."""
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = UsersSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipes_in'
    )
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'tags', 'image', 'cooking_time',
            'author', 'text', 'ingredients', 'pub_date',
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = (
            'pub_date', 'author'
        )

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and obj.favorites_recipes.filter(
                user=self.context.get('request').user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and obj.shopping_recipe.filter(
                user=self.context.get('request').user, recipe=obj).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    name = serializers.CharField()

    class Meta:
        model = Recipe
        fields = (
            'name', 'tags', 'image', 'text',
            'cooking_time', 'ingredients', 'author'
        )
        read_only_fields = ('author',)

    @transaction.atomic
    def create_ingredient_in_recipe_set_tags(self, ingredients, recipe, tags):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']
            )for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredient_in_recipe_set_tags(ingredients, recipe, tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.get('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.create_ingredient_in_recipe_set_tags(ingredients, instance, tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
