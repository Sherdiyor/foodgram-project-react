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


class UserFollowSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        return obj.following.filter(
            follower=self.context.get('request').user
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        if limit:
            try:
                queryset = Recipe.objects.filter(author=obj)[:int(limit)]
            except TypeError:
                serializers.ValidationError(
                    'Значение limit является объектом NoneType')
        else:
            queryset = Recipe.objects.filter(author=obj)
        return FollowRecipeSerializer(queryset, many=True).data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
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
