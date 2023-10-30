from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (UsersViewSet,
                    IngredientViewSet,
                    TagViewSet,
                    RecipesViewSet)


app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(r"users", UsersViewSet, basename="users")
v1_router.register(r"ingredients", IngredientViewSet, basename="ingredients")
v1_router.register(r"recipes", RecipesViewSet, basename="recipes")
v1_router.register(r"tags", TagViewSet, basename="tag")


urlpatterns = [
    path("", include(v1_router.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include("djoser.urls.authtoken")),
]
