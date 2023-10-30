from posts.models import Tags
from django.core.exceptions import ValidationError


class ValidationTagIngredient:

    def tag_validator(tag_input):
        if not tag_input:
            raise ValidationError("Укажите теги")
        for tag in tag_input:
            if not Tags.objects.filter(name=tag).exists():
                raise ValidationError(
                    {"error": "Такого тэга не существует"}
                )
        return tag_input

    def ingredient_validator(ingredients):
        if not ingredients:
            raise ValidationError("Укажите ингридиенты")
        ingredient_total = []
        for ingredient_item in ingredients:
            ingredient_id = ingredient_item["ingredient"]["id"]
            if ingredient_id in ingredient_total:
                raise ValidationError(
                    "Ингредиент должен быть уникальным!")
            ingredient_total.append(ingredient_item)
        return ingredient_total
