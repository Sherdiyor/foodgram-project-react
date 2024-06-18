from rest_framework import mixins, viewsets

from .filters import IngredientsSearchFilter
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
)
from .models import Ingredient, Tag, Recipe
from users.pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly


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


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    ordering_fields = ("-pub_date",)
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method is "GET":
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.request.user.is_authenticated:
            if self.request.query_params.get("is_favorite"):
                queryset = queryset.filter(favorites__user=self.request.user)
            if self.request.query_params.get("in_is_shopping_cart"):
                queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset
