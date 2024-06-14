from rest_framework import serializers
from .models import Favorite, Tag, Ingredient, Recipe, RecipeIngredient, ShoppingCart
from djoser.serializers import UserCreateSerializer, UserSerializer


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
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amouont")


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredient = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    image = serializers.ImageField(
        max_length=None, use_url=True, allow_null=True, required=False
    )

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

    def validate_tags(self, tags):
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
        if not ingredients:
            raise serializers.ValidationError("Должен быть хотя бы 1 ингредиент")

    def create_ingredients(recipe, ingredients):
        ing_list = []
        for ingredient in ingredients:
            ing_list.append(
                RecipeIngredientSerializer(
                    ingredient=ingredient.pop("id"),
                    amount=ingredient.pop("amount"),
                    recipe=recipe,
                )
            )
        RecipeIngredientSerializer.objects.bulk_create(ing_list)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
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
            "ingredients",
            "tags",
            "author",
            "image",
            "name",
            "text",
            "cooking_time",
            "pub_date",
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
        return obj.cart.filter(user=request.user).exists()


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe")

    def validate(self, data):
        user = data["user"]
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError("Рецепт уже есть в избранном")


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ("id", "user", "recipe")

    def validate(self, data):
        user = data["user"]
        if user.shopping_cart.filter(recipe=data["recipe"]).exists():
            raise serializers.ValidationError("Рецепт уже добавлен в список покупок")
