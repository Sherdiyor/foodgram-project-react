from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")

    def validate_amount(self, amount):
        if amount < 1:
            raise serializers.ValidationError(
                "Количество ингредиентов должно быть больше 1")
        return amount


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "author",
            "image",
            "name",
            "text",
            "cooking_time",
            "pub_date",
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    def validate_tags(self, tags):
        tags_len = len(tags)
        if not tags:
            raise serializers.ValidationError(
                "Нельзя создать рецепт без тегов"
            )
        if tags_len != len(set(tags)):
            raise serializers.ValidationError(
                "Теги не должны повторяться"
            )
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError("Такого тега не существует")
        return tags

    def validate_name(self, name):
        if len(name) < 1:
            raise serializers.ValidationError(
                "Поле name должно содержать хотя бы одну букву"
            )
        return name

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть больше одной минуты"
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredients_len = len([ingredient.get("id")
                              for ingredient in ingredients])
        if not ingredients:
            raise serializers.ValidationError(
                "Должен быть хотя бы 1 ингредиент")
        if ingredients_len != len(
            set([ingredient.get("id") for ingredient in ingredients])
        ):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться"
            )
        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ing_list = []
        for ingredient_data in ingredients:
            ing_list.append(
                RecipeIngredient(
                    ingredient=ingredient_data.pop("id"),
                    amount=ingredient_data.pop("amount"),
                    recipe=recipe,
                )
            )
        RecipeIngredient.objects.bulk_create(ing_list)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.tags.set(tags)
        if not (ingredients or tags):
            raise serializers.ValidationError(
                "Ингредиенты или теги отсутствуют"
            )
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=False)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorite",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return (
            ShoppingCart.objects.filter(
                recipe_id=obj.id, user=request.user).exists()
        )


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe")

    def validate(self, data):
        user = data["user"]
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError("Рецепт уже есть в избранном")
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ("id", "user", "recipe")

    def validate(self, data):
        user = data["user"]
        recipe_id = data["recipe"].id
        if (
            ShoppingCart.objects.filter(
                user=user, recipe__id=recipe_id).exists()
        ):
            raise serializers.ValidationError(
                "Рецепт уже добавлен в список покупок")
        return data
