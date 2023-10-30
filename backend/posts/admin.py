from django.contrib import admin

from .models import Ingredients, Recipes, Tags


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ["name", "author"]
    search_fields = ["author", "name", "tag"]
    list_filter = ["author", "name", "tags"]


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    search_fields = ["name"]
    list_filter = ["name", ]


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    pass
