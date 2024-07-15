from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from users.models import Follow, User


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
        return obj.following.filter(follower=request.user,
                                    following=obj.id).exists()

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


class UserFollowSerializer(serializers.ModelSerializer):
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


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
            "id",
            "following",
            "follower",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('follower', 'following'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == self.context.get('following'):
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserFollowSerializer(
            instance.following, context={'request': request}
        ).data
