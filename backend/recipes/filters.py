from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientsSearchFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(FilterSet):
    author = CharFilter()
    tags = CharFilter()
    is_favorited = BooleanFilter(method='get_favorite')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_cart')

    class Meta:
        model = Recipe()
        fields = (
            "author",
            "tags"
        )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset
