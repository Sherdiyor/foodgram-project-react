from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from recipes.constants import MAX_EMAIL_LENGTH, MAX_NAMES_LENGTH

from .validators import validate_name


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    email = models.EmailField(
        unique=True, verbose_name="почта", max_length=MAX_EMAIL_LENGTH)
    username = models.CharField(
        unique=True,
        verbose_name="никнэйм",
        max_length=MAX_NAMES_LENGTH,
        validators=[
            RegexValidator(regex=r'[\w.@+-]+',  # r'^[w.@+-]+Z'
                           message="Не корректное имя пользователя"),
            validate_name
        ]
    )
    first_name = models.CharField(
        verbose_name="имя", max_length=MAX_NAMES_LENGTH)
    last_name = models.CharField(
        verbose_name="фамилия", max_length=MAX_NAMES_LENGTH)

    class Meta:
        verbose_name = "Пользователь"
        ordering = ("-id",)

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
        ordering = ("following",)
