from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, TagViewSet, RecipeViewSet


router = DefaultRouter()
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("tags", TagViewSet, "tags")
router.register("recipes", RecipeViewSet, "recipes")


urlpatterns = [path("api/", include(router.urls))]
