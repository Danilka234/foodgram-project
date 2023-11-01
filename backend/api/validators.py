from django.core.exceptions import ValidationError
from posts.models import Tags


class ValidationTagIngredient:

    def tag_validator(tag_input):
        if not tag_input:
            raise ValidationError("Укажите теги")
        tag_total = []
        for tag in tag_input:
            if not Tags.objects.filter(name=tag).exists():
                raise ValidationError(
                    {"error": "Такого тэга не существует"}
                )
        for tag in tag_input:
            if tag in tag_total:
                raise ValidationError(
                    "Не выбирайте один и тот же тэг для рецепта."
                )
            tag_total.append(tag)
        return tag_input

    def ingredient_validator(ingredients):
        if not ingredients:
            raise ValidationError("Укажите ингридиенты")
        ingredient_total = []
        for ingredient_item in ingredients:
            ingredient_amount = ingredient_item["amount"]
            if ingredient_amount < 1:
                raise ValidationError(
                    "Необходимо добавить хотя бы щепотку игредиента!"
                )
            if ingredient_item in ingredient_total:
                raise ValidationError(
                    "Ингредиент должен быть уникальным!")
            ingredient_total.append(ingredient_item)
        return ingredient_total
