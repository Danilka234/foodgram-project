from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from djoser.views import UserViewSet
from django.db.models import Sum, F
from django_filters.rest_framework import DjangoFilterBackend


from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.validators import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions, exceptions

from users.models import User
from posts.models import Recipes, Tags, Ingredients, Favorite, Subscribe, ShoppingList, AmountOfIngridient
from .serializers import (RecipesPostSerializer,
                          RecipesListSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          SubscribeSerializer,
                          ShortRecipeSerializer,
                          )
from .permissions import IsAuthorOrAdminOrReadOnly, IsAdminOrReadOnly
from .filters import RecipeFilter, IngredientFilter
from .paginations import CustomPagination


class UsersViewSet(UserViewSet):
    """Получение информации, поиск и редактирование
    пользователей."""
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = CustomPagination
    
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get("id"))
        subscription, created = Subscribe.objects.get_or_create(
            user=request.user,
            author=author
        )
        if (author == request.user):
            raise exceptions.ValidationError(
                detail="Подписаться на себя не возможно!"
            )
        if request.method == "POST" and not created:
            raise exceptions.ValidationError(
                detail="Вы уже подписались на данного автора!"
            )
        if request.method == "POST":
            serializer = SubscribeSerializer(
                author,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE" and not subscription:
            raise exceptions.ValidationError(
                detail="Вы не подписывались на этого автора."
            )
        if request.method == "DELETE":
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(author__user=self.request.user)
        serializer = SubscribeSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if  self.request.method == "GET":
            return RecipesListSerializer
        return RecipesPostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=["POST", "DELETE"],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        favorite_recipe, created = Favorite.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if request.method == "POST" and not created:
            raise exceptions.ValidationError(
                detail="Вы уже добавили этот рецепт в избранное!"
            )
        if request.method == "POST":
            serializer = ShortRecipeSerializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == "DELETE":
            favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=["POST", "DELETE"],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.add_cart(ShoppingList, request.user, pk)
        if request.method == "DELETE":
            return self.delete_cart(ShoppingList, request.user, pk)

    def add_cart(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({"errors": "Вы уже добавили этот рецепт в список покупок."},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipes, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_cart(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"errors": "Вы уже удалили данный рецепт."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=["GET"],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        shop_user = request.user
        if not shop_user.shopping_user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = AmountOfIngridient.objects.filter(
            recipe__shopping_recipe__user=shop_user
        ).values(
            name=F("ingredient__name"),
            measurement_unit=F("ingredient__measurement_unit")
        ).annotate(amount=Sum("amount"))
        shop_list = (f"Моя корзина.\n\n")
        shop_list += "\n".join([
            f'* {ingredient["name"]} '
            f'({ingredient["measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
            
        ])
        today = datetime.today()
        file = f"Список покупок от {today:%Y-%m-%d}.txt"
        response = HttpResponse(shop_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
