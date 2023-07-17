from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet, UsersViewSet
)

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),
]


