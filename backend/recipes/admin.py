from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient


class TagInline(admin.TabularInline):
    model = RecipeTag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "text",
        "author",
        "pub_date",
    )
    search_fields = ("name", "author__username")
    inlines = [
        IngredientInline,
        TagInline,
    ]
