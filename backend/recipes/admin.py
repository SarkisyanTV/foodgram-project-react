from django.contrib import admin

from .models import (
    Recipe, Tag, RecipeIngredient, ShoppingCart,
    Favorite, Subscribe
)

# Register your models here.
admin.site.register(
    Recipe,
    list_display=(
        'id', 'name',  'image', 'pub_date', 'author'),
    filter=('author',)
    )
admin.site.register(Tag, list_display=('name', 'color', 'slug'))
admin.site.register(Favorite, list_display=('recipe', 'user'))
admin.site.register(
    RecipeIngredient,
    list_display=('recipe', 'ingredient', 'amount')
)
admin.site.register(ShoppingCart, list_display=('recipe', 'user'))
admin.site.register(
    Subscribe, list_display=('user', 'author')
)
