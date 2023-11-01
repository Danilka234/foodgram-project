from django.contrib import admin

from .models import User
from posts.models import Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']
    ordering = ['username']


@admin.register(Subscribe)
class UserSubscribeAdmin(admin.ModelAdmin):
    list_display = ["user", "author"]
