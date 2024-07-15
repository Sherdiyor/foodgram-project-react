from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (MAX_COLOR_FIELD_LENGTH, MAX_FILED_LENGTH,
                               MAX_TEXT_LENGTH, MIN_COOKING_TIME)
from users.models import User


class Tag(models.Model):
    name = models.CharField("название", unique=True,
                            max_length=MAX_FILED_LENGTH)
    color = ColorField(
        unique=True,
        max_length=MAX_COLOR_FIELD_LENGTH,
        verbose_name="поле цвета"
    )
    slug = models.SlugField(max_length=MAX_FILED_LENGTH)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name[:MAX_TEXT_LENGTH]


class Ingredient(models.Model):
    name = models.CharField("название", max_length=MAX_FILED_LENGTH)
    measurement_unit = models.CharField(
        "еденица измерения", max_length=MAX_FILED_LENGTH)

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        constraints = [models.UniqueConstraint(
            fields=("name", "measurement_unit"), name="Uniqe_validated"
        )]

    def __str__(self):
        return self.name[:MAX_TEXT_LENGTH]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes")
    image = models.ImageField(upload_to="images", blank=True)
    name = models.CharField(
        "название", unique=True,
        max_length=MAX_FILED_LENGTH
    )
    text = models.TextField("описание рецепта", )
    cooking_time = models.PositiveIntegerField(
        "время приготовления",
        validators=[
            MinValueValidator(MIN_COOKING_TIME)
        ]
    )
    pub_date = models.DateTimeField(
        "дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name[:MAX_TEXT_LENGTH]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    amount = models.PositiveIntegerField(
        verbose_name="количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="recipe_ingredients"
            )
        ]

    def __str__(self):
        return self.ingredient[:MAX_TEXT_LENGTH]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        ordering = ("recipe", "user")
        verbose_name = "Избранное"
        constraints = [
            models.UniqueConstraint(fields=["recipe", "user"], name="favorite")
        ]

    def __str__(self) -> str:
        return self.recipe[:MAX_TEXT_LENGTH]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="рецепты в корзине",
        related_name="shopping_carts",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="владелец корзины",
        related_name="shopping_carts",
    )

    class Meta:
        verbose_name = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "user"), name="recipe_is_in_cart")
        ]
        ordering = ('user__username',)

    def __str__(self):
        return f"{self.recipe} находится в корзине у {self.user}"
