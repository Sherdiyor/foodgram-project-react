from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("tags", TagViewSet, "tags")
router.register("recipes", RecipeViewSet, "recipes")


urlpatterns = [path("", include(router.urls))]
