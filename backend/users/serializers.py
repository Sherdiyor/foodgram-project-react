from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

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
        return False if not request.user.is_authenticated else (
            obj.following.filter(follower=request.user,
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
    recipes_count = serializers.ReadOnlyField(source="following.recipes_count")
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

    def validate(self, data):
        user = self.context.get('request').user
        following = data.get('following')
        if user == following:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'})
        if Follow.objects.filter(follower=user, following=following).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного пользователя'})
        return data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            follower=obj.follower, following=obj.following
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.following)
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except TypeError:
                serializers.ValidationError(
                    'Значение limit является объектом NoneType')
        return FollowRecipeSerializer(queryset, many=True).data
