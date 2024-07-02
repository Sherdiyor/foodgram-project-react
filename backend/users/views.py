from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .pagination import CustomPagination
from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(User, id=id)

        if user == following:
            return Response(
                {"errors": "вы не можете подписаться сами на себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(follower=user, following=following).exists():
            return Response(
                {"errors": "вы уже подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.create(follower=user, following=following)
        serializer = FollowSerializer(
            follow,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        serializer_class=FollowSerializer,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        query = Follow.objects.filter(follower=request.user)
        paginated_content = self.paginate_queryset(queryset=query)
        serializer = FollowSerializer(
            paginated_content, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(User, pk=id)
        subscribe = get_object_or_404(
            Follow, follower=user, following=following)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
