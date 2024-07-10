from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.pagination import CustomPagination

from .filters import IngredientsSearchFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, TagSerializer)


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
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
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
                queryset = queryset.filter(
                    shopping_cart__user=self.request.user)
        return queryset

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {"user": user.id, "recipe": recipe.id}
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorite, user=request.user, recipe=get_object_or_404(
                Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        user = request.user
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {"user": user.id, "recipe": recipe.id}
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart, user=request.user, recipe=get_object_or_404(
                Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__in_cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(ingredient_amount=Sum("amount"))
        )
        shopping_list = ["Список покупок:\n"]
        for ingredient in ingredients:
            name = ingredient["ingredient__name"]
            unit = ingredient["ingredient__measurement_unit"]
            amount = ingredient["ingredient_amount"]
            shopping_list.append(f"\n{name} - {amount}, {unit}")
        response = FileResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
