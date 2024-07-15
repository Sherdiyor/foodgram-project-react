from django_filters.rest_framework import (AllValuesFilter, BooleanFilter,
                                           FilterSet)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientsSearchFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(FilterSet):
    tags = AllValuesFilter(field_name="tags__slug")
    is_favorited = BooleanFilter(method='get_favorite')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_cart')

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset
