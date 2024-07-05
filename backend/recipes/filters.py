from django_filters.rest_framework import CharFilter, FilterSet
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientsSearchFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(FilterSet):
    author = CharFilter()
    tags = CharFilter()

    class Meta:
        model = Recipe()
        fields = (
            "author",
            "tags"
        )
