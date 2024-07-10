from recipes.models import Recipe
from rest_framework import serializers

from .models import Follow, User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return (
            Follow.objects.filter(follower=request.user,
                                  following=obj.id).exists()
        )

    def validate_username(self, username):
        if username == "me":
            raise serializers.ValidationError(
                "Вы не можете создать пользователя с ником me")
        return username


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source="following.id")
    email = serializers.ReadOnlyField(source="following.email")
    username = serializers.ReadOnlyField(source="following.username")
    first_name = serializers.ReadOnlyField(source="following.first_name")
    last_name = serializers.ReadOnlyField(source="following.last_name")

    class Meta:
        model = Follow
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            follower=obj.follower, following=obj.following
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.following)
        if limit:
            queryset = queryset[: int(limit)]
        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()
