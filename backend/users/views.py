from djoser.views import UserViewSet
from .models import User, Follow
from .serializers import CustomUserSerializer, FollowSerializer, FollowRecipeSerializer
from .pagination import CustomPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(detail=False, permission_classes=IsAuthenticated)
    def following(self, request):
        queryset = Follow.objects.filter(follower=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages, context={"request": request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def follow(self, request, id):
        user = request.user
        author = get_object_or_404(user, pk=id)
        if request.method == "POST":
            serializer = FollowRecipeSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(follower=user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            get_object_or_404(Follow, follower=user, following=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
