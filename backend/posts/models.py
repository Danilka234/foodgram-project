from django.db import models
from users.models import User


class Tags(models.Model):
    """Модель тэга для рецепта."""
    name = models.CharField(
        verbose_name="Название тэга",
        max_length=70,
        unique=True
    )
    slug = models.SlugField(
        verbose_name="slug",
        unique=True)
    color = models.CharField(
        verbose_name="Цвет",
        unique=True,
        max_length=10
    )

    class Meta:
        ordering = ("name", )
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self) -> str:
        return self.name


class Ingredients(models.Model):
    """Модель ингридиентов."""
    name = models.CharField(
        verbose_name="Ингридиент",
        max_length=70
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=20
    )

    class Meta:
        ordering = ("name", )
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self) -> str:
        return f"{self.name}, {self.measurement_unit}"


class Recipes(models.Model):
    """Модель рецетов."""
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="автор"
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200
    )
    description = models.CharField(
        verbose_name="Описание",
        max_length=300
    )
    tags = models.ManyToManyField(
        Tags,
        related_name="tag",
        verbose_name="Тэг"
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through="AmountOfIngridient",
        verbose_name="Ингридиент"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )
    image = models.ImageField(
        verbose_name="Изображение блюда",
        upload_to="recipe/"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        default=1
    )

    class Meta:
        ordering = ("-pub_date", )
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self) -> str:
        return self.name


class AmountOfIngridient(models.Model):
    """Модель кол-ва ингридинтов в описанном рецепте."""
    ingredient = models.ForeignKey(
        Ingredients,
        related_name="ingredient",
        on_delete=models.CASCADE,
        verbose_name="Инридиент"
    )
    recipe = models.ForeignKey(
        Recipes,
        related_name="ingredient_in_recipe",
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Кол-во ингридиента",
        default=1
    )

    class Meta:
        ordering = ("recipe", )
        verbose_name = "Кол-во ингридиента"
        verbose_name_plural = "Кол-во ингридиентов"

    def __str__(self) -> str:
        return f"{self.ingredient} {self.amount}"


class Favorite(models.Model):
    """Модель с любимыми рецептами."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Понравившийся рецепт")

    class Meta:
        verbose_name = "Понравившийся рецепт"
        verbose_name_plural = "Понравившиеся рецепты"
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"],
                                    name="unique_favorite"),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.recipe}"


class Subscribe(models.Model):
    """Подписки для авторов."""
    user = models.ForeignKey(
        User,
        related_name="subscriber",
        on_delete=models.CASCADE,
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        related_name="author",
        on_delete=models.CASCADE,
        verbose_name="Автор поста"
    )
    created = models.DateTimeField(
        "Дата подписки на автора",
        auto_now_add=True)

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        return f"{self.user} {self.author}"


class ShoppingList(models.Model):
    """Модель рецептов помещенных в корзину."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        null=True,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Покупка')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-id']

    def __str__(self):
        return f"{self.user} {self.recipe}"
