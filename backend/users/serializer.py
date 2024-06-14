from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import User, Follow


class CustomUserSerializer(UserSerializer):
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
        if request.user.is_anonymous:
            return False
        else:
            return Follow.objects.filter(user=request.user, following=obj.id).exists()
