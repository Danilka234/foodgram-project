from posts.models import Tags, Ingredients
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404



class ValidationTagIngredient:

    def tag_validator(tag_input):
        # print(tag_input)
        if not tag_input:
            raise ValidationError("Укажите теги")
        # tags = Tags.objects.filter(id__in=tag_input).exists()
        for tag in tag_input:
            # print(tag)
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
            ingredient_id = ingredient_item['ingredient']['id']
            if ingredient_id in ingredient_total:
                raise ValidationError(
                    'Ингредиент должен быть уникальным!')
            # print(ingredient_id)
            ingredient_total.append(ingredient_item)
        #     print(ingredient_item)
        #     print()
        # print(ingredient_total)
        # print()
        return ingredient_total    
