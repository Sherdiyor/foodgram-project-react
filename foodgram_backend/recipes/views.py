from rest_framework import mixins, viewsets

from foodgram_backend.recipes.filters import IngredientsSearchFilter
from foodgram_backend.recipes.serializers import IngredientSerializer
from .models import Ingredient


class GETViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    pass


class IngredientViewSet(GETViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ("^name",)
