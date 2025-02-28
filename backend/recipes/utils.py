from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def shopping_or_favorite(request, pk, serializer):
    user = request.user
    context = {"request": request}
    try:
        recipe = Recipe.objects.get(id=pk)
    except Recipe.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    data = {"user": user.id, "recipe": recipe.id}
    serializer = serializer(data=data, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def favorite_or_shopping_delete(request, pk, model):
    mod = model.objects.filter(user=request.user, recipe=get_object_or_404(
        Recipe, id=pk)
    )
    if mod.exists():
        mod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def shopping_cart_file(request, ingredients):
    shopping_list = ["Список покупок:\n"]
    for ingredient in ingredients:
        name = ingredient["ingredient__name"]
        unit = ingredient["ingredient__measurement_unit"]
        amount = ingredient["ingredient_amount"]
        shopping_list.append(f"\n{name} - {amount}, {unit}")
    response = FileResponse(shopping_list, content_type="text/plain")
    response["Content-Disposition"] = (
        'attachment; filename="shopping_cart.txt"'
    )
    return response
