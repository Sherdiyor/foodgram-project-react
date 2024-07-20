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
        return (
            request.user.is_authenticated
            and obj.following.filter(follower=request.user).exists()

        )


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

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = obj.recipes.all()

        if limit.isdigit():
            queryset = obj.recipes.all()[:int(limit)]

        return FollowRecipeSerializer(
            queryset, many=True, context={"request": request}
        ).data


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

    def to_representation(self, instance):
        return UserFollowSerializer(
            instance.following, context={
                'request': self.context.get('request')}
        ).data
