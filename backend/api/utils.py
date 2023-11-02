from datetime import datetime

from django.db.models import F, Sum
from django.http import HttpResponse

from posts.models import AmountOfIngridient


def download_cart(recipes):
    shop_list = ("Моя корзина.\n\n")
    for recipe in recipes:
        shop_list += f"{recipe.name}:\n"
        ingredients = AmountOfIngridient.objects.filter(recipe=recipe).values(
            name=F("ingredient__name"),
            measurement_unit=F("ingredient__measurement_unit")
        ).annotate(amount=Sum("amount"))
        shop_list += "\n".join([
            f"* {ingredient['name']} "
            f"({ingredient['measurement_unit']})"
            f" - {ingredient['amount']}"
            for ingredient in ingredients

        ])
        shop_list += "\n\n"
    today = datetime.today()
    file = f"Список покупок от {today:%Y-%m-%d}.txt"
    response = HttpResponse(shop_list, content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename={file}"
    return response
