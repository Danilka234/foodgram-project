import base64

import webcolors

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer

from .validators import ValidationTagIngredient
from users.models import User
from posts.models import (Recipes, Tags, Ingredients,
                          Subscribe, Favorite,
                          AmountOfIngridient,
                          ShoppingList)


class CreateUserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username",
                  "email", "first_name",
                  "last_name", "password",
                  "is_subscribed")
        extra_kwargs = {"password": {"write_only": True}}
    
    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        if Subscribe.objects.filter(
            user=current_user, author=obj.id
        ).exists():
            return True
        return False


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',
                  "is_subscribed")
        # read_only_fields = ("is_subscribed",)
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("subscriber", "user"),
                message="Вы уже подписанны на данного автора!"
            )
        ]

    def validate(self, data):
        if data["user"] == data["subscriber"]:
            raise serializers.ValidationError(
                "Подписаться на себя не возможно!"
            )
        return data

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        if Subscribe.objects.filter(
            user=current_user, author=obj.id
        ).exists():
            return True
        return False


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class AmountOfIngridientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source="ingredient.name"
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = AmountOfIngridient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipesListSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра одного или множества рецептов."""
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    text = serializers.CharField(source="description")
    image = Base64ImageField(required=False)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart",
                  "name", "image", "text", "cooking_time")
        
    def get_ingredients(self, recipe: Recipes):
        ingredients = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("ingredient__amount")
        )
        return ingredients

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=current_user,
            recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=current_user,
            recipe=obj).exists()


class RecipesPostSerializer(serializers.ModelSerializer):
    """Сериалайзер для обновления, создания рецептов."""
    ingredients = AmountOfIngridientSerializer(many=True,
                                               source='ingredient_in_recipe')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    images = Base64ImageField(required=False)
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    text = serializers.CharField(source="description")

    class Meta:
        model = Recipes
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart",
                  "name", "images", "text", "cooking_time")
    
    
    def validate(self, data):
        ingredients = data.get("ingredient_in_recipe")
        cooking_time = data.get("cooking_time")
        tags = data.get("tags")
        tags = ValidationTagIngredient.tag_validator(tags)
        ingredients = ValidationTagIngredient.ingredient_validator(
            ingredients
        )
        if cooking_time <= 0:
            raise serializers.ValidationError(
                {'error': 'Время приготовления должно быть не менее 1 мин.'})
        data["ingredient_in_recipe"] = ingredients
        return data
    
    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=current_user,
            recipe=obj.id).exists()
    
    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=current_user,
            recipe=obj).exists()
        
    @staticmethod
    def save_ingredients(recipe, ingredients):
        for ingredient in ingredients:
            AmountOfIngridient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get("ingredient").get("id"),
                amount=ingredient.get("amount")
            )
        
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredient_in_recipe")
        tags = validated_data.pop("tags")
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients(recipe, ingredients)
        return recipe
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.description = validated_data.get("description", instance.description)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        ingredients = validated_data.pop("ingredient_in_recipe")
        tags = validated_data.pop("tags")
        if "tags" in validated_data:
            instance.tags.set(tags)
        instance.ingredients.clear()
        self.save_ingredients(instance, ingredients)
        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")

    
class SubscribeSerializer(serializers.ModelSerializer):
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        model = User
    
    def get_recipes(self, obj):
        recipes_limit = self.context.get("request").query_params.get(
            "recipes_limit"
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return recipes

    
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    

    def get_is_subscribed(self, obj):
        current_user = self.context["request"].user
        if current_user.is_anonymous:
            return False
        if Subscribe.objects.filter(
            user=current_user, author=obj.id
        ).exists():
            return True
