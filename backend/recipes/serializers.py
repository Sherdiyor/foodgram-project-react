from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import MIN_AMOUNT
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
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
        if amount < MIN_AMOUNT:
            raise serializers.ValidationError(
                f"Количество ингредиентов должно быть больше {MIN_AMOUNT}"
            )
        return amount


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None)
    cooking_time = serializers.IntegerField()

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
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < MIN_AMOUNT:
            raise serializers.ValidationError(
                f"Время приготовления должно быть больше {MIN_AMOUNT} минуты"
            )
        return cooking_time

    def validate(self, data):
        ingredients = data.get("ingredients")
        ingredients_ids = [ingredient.get("id")
                           for ingredient in ingredients]
        if not ingredients:
            raise serializers.ValidationError(
                "Должен быть хотя бы 1 ингредиент")
        if len(ingredients_ids) != len(
            set(ingredients_ids)
        ):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться"
            )
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ing_list = [
            RecipeIngredient(
                ingredient=ingredient_data.pop("id"),
                amount=ingredient_data.pop("amount"),
                recipe=recipe,
            )
            for ingredient_data in ingredients
        ]
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
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get("request")

        return (
            obj.favorites.filter(user=request.user).exists()
            and request.user.is_authenticated
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request.user.shopping_carts.filter(recipe=obj).exists()
            and request.user.is_authenticated
        )


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def validate(self, data):
        user = data["user"]
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError("Рецепт уже есть в избранном")
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

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
