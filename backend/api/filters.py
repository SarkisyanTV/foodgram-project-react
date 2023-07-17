from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites_recipes__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_recipe__user=user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для поиска ингредиентов."""
    name = filters.CharFilter(
        field_name='name', method='name_filter'
    )

    def name_filter(self, queryset, name, value):
        return queryset.filter(name__istartswith=value)

    class Meta:
        model = Ingredient
        fields = ('name',)
