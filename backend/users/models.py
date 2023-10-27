# from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
# from foodgram_backend.foodgram.models import Recipes


class User(AbstractUser):
    """Модель пользователя.
    Включает дополнительные функции.
    """
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    username = models.CharField(
        # validators=(validate_username_own,),
        verbose_name="Пользователь",
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        verbose_name="email пользователя",
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        verbose_name="Имя пользователя",
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name="Фамилия пользователя",
        max_length=150,
        blank=False
    )

    class Meta:
        ordering = ("username", )
        verbose_name = "Пользователь"

    def __str__(self):
        return self.username
