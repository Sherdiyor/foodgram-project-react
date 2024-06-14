from rest_framework import mixins, viewsets

from .filters import IngredientsSearchFilter
from .serializers import IngredientSerializer, TagSerializer
from .models import Ingredient, Tag


class GETViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    pass


class IngredientViewSet(GETViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ("^name",)


class TagViewSet(GETViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
