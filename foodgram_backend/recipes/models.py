from django.db import models
from colorfield.fields import ColorField
from users.models import User


class Tag(models.Model):
    name = models.CharField("название", unique=True, max_length=200)
    color = ColorField()
    slug = models.SlugField(max_length=200)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тэг"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField("название", unique=True, max_length=200)
    measurement_unit = models.CharField("еденица измерения", max_length=200)

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингридиент"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    image = models.ImageField(upload_to="images", blank=True)
    name = models.CharField("название", unique=True, max_length=200)
    text = models.CharField("описание рецепта", max_length=200)
    cooking_time = models.PositiveIntegerField("время приготовления")
    pub_date = models.DateTimeField("дата публикации", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipeingredient"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipeingredient"
    )
    amount = models.PositiveIntegerField(verbose_name="количество")

    class Meta:
        verbose_name = "Ингридиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="recipeingredient"
            )
        ]

    def __str__(self):
        return self.ingredient


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")

    class Meta:
        ordering = ("recipe", "user")
        verbose_name = "Избранное"
        constraints = [
            models.UniqueConstraint(fields=["recipe", "user"], name="favorite")
        ]
