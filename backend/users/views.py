from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DJUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .pagination import UserRecipePagination
from .serializers import FollowSerializer, UserSerializer


class UserViewSet(DJUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserRecipePagination
    permission_classes = [AllowAny]

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(User, id=id)
        follow = {'follower': user, 'following': following}
        serializer = FollowSerializer(
            data=follow,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=UserSerializer,
    )
    def me(self, request, pk=None):
        return Response(
            self.get_serializer(request.user).data, status.HTTP_200_OK
        )
