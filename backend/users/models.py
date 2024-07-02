from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="почта", max_length=254)
    username = models.CharField(
        blank=False, unique=True, verbose_name="никнэйм", max_length=150
    )
    first_name = models.CharField(blank=False, verbose_name="имя", max_length=150)
    last_name = models.CharField(blank=False, verbose_name="фамилия", max_length=150)
    shopping_cart = models.ManyToManyField(
        "recipes.Recipe",
        verbose_name="корзина покупок",
        blank=True,
        related_name="users",
    )
    favorite = models.ManyToManyField(
        "recipes.Recipe", blank=True, verbose_name="список избранного"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        verbose_name = "Подписка"
