from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DJUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Follow, User
from users.pagination import UserRecipePagination
from users.serializers import (FollowSerializer, UserFollowSerializer,
                               UserSerializer)


class UserViewSet(DJUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserRecipePagination
    permission_classes = [AllowAny]

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        following = get_object_or_404(User, id=id)
        follow_data = {"following": following.id, "follower": request.user.id}
        serializer = FollowSerializer(
            data=follow_data,
            context={"request": request, 'following': following},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'Failure': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        serializer_class=FollowSerializer,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        query = User.objects.filter(following__follower=request.user)
        paginated_content = self.paginate_queryset(queryset=query)
        serializer = UserFollowSerializer(
            paginated_content, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(User, pk=id)
        subscribe = Follow.objects.filter(follower=user, following=following)
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=UserSerializer,
    )
    def me(self, request, pk=None):
        data = UserSerializer(
            request.user,
            context={
                'request': request
            }
        ).data
        return Response(
            data, status=200
        )
