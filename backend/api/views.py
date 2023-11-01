from datetime import datetime

from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from posts.models import (AmountOfIngridient, Favorite, Ingredients, Recipes,
                          ShoppingList, Subscribe, Tags)
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipesListSerializer,
                          RecipesPostSerializer, ShortRecipeSerializer,
                          SubscribeSerializer, TagSerializer)


class UsersViewSet(UserViewSet):
    """Получение информации, поиск, редактирование
    пользователей и подписки для пользователей."""
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Переопределение пермишена для анонима на endpoint 'api/users/me/'
        """
        if self.action == "me":
            self.permission_classes = (permissions.IsAuthenticated, )
        return super().get_permissions()

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Подписка для пользователей.
        Пример endpoint:
            api/users/2/subscribe/
            2 = pk пользователя.
        """
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=request.user,
            author=author
        )
        if (author == request.user):
            raise exceptions.ValidationError(
                detail="Подписаться на себя не возможно!"
            )
        if request.method == "POST" and subscription.exists():
            raise exceptions.ValidationError(
                detail="Вы уже подписались на данного автора!"
            )
        if request.method == "POST":
            serializer = SubscribeSerializer(
                author,
                context={"request": request}
            )
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE" and not subscription.exists():
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
        """Список подписок пользователя.
        Пример endpoint:
            api/users/subscriptions/
        """
        queryset = User.objects.filter(author__user=self.request.user)
        serializer = SubscribeSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class RecipesViewSet(viewsets.ModelViewSet):
    """Работа с рецептыми, создание, удаление, добавление в избранное
    и корзину.
    """
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    http_method_names = ("get", "post", "patch", "delete")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipesListSerializer
        return RecipesPostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=["POST", "DELETE"],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        """Функция для добавления и удаления рецепта в/из избранные."""
        user = self.request.user
        if request.method == "POST":
            favorite_recipe = Favorite.objects.filter(
                recipe__id=pk, user=user
            )
            if favorite_recipe.exists():
                return Response(
                    {"error": "Вы уже добавили этот рецепт в избранное!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                recipe = Recipes.objects.get(pk=pk)
            except Recipes.DoesNotExist:
                return Response(
                    {"errors": "Такого рецепта не существует!."},
                    status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == "DELETE":
            try:
                recipe = Recipes.objects.get(pk=pk)
            except Recipes.DoesNotExist:
                return Response(
                    {"errors": "Такого рецепта не существует!."},
                    status=status.HTTP_404_NOT_FOUND)
            favorite_recipe = Favorite.objects.filter(
                recipe__id=pk, user=user
            )
            if favorite_recipe.exists():
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"error": ("Вы еще не добавляли этот рецепт "
                                       "в избранное!")},
                            status=status.HTTP_400_BAD_REQUEST
                            )

    @action(detail=True,
            methods=["POST", "DELETE"],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Функция добавления рецепта в список покупок."""
        if request.method == "POST":
            return self.add_cart(ShoppingList, request.user, pk)
        if request.method == "DELETE":
            return self.delete_cart(ShoppingList, request.user, pk)

    def add_cart(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "Вы уже добавили этот рецепт в список покупок."},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe = Recipes.objects.get(pk=pk)
        except Recipes.DoesNotExist:
            return Response(
                {"errors": "Такого рецепта не существует!."},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_cart(self, model, user, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        cart = model.objects.filter(user=user, recipe=recipe)
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"errors": "Вы уже удалили данный рецепт."},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=["GET"],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Функция скачивания рецептов из списка покупок."""
        shop_user = request.user
        if not shop_user.shopping_user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = AmountOfIngridient.objects.filter(
            recipe__shopping_recipe__user=shop_user
        ).values(
            name=F("ingredient__name"),
            measurement_unit=F("ingredient__measurement_unit")
        ).annotate(amount=Sum("amount"))
        shop_list = ("Моя корзина.\n\n")
        shop_list += "\n".join([
            f'* {ingredient["name"]} '
            f'({ingredient["measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients

        ])
        today = datetime.today()
        file = f"Список покупок от {today:%Y-%m-%d}.txt"
        response = HttpResponse(shop_list, content_type='text/plain')
        response["Content-Disposition"] = f"attachment; filename={file}"
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс для работы с тегами.
    Создание и редактирование доступно только администратору.
    """
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс для работы с ингредиентами.
    Создание и редактирование доступно только администратору.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
