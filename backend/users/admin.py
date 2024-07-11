from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "username", "first_name",
                    "last_name", "num_followers", "num_recipes")
    search_fields = ("username", "email")

    def num_followers(self, obj):
        return obj.follower.count()

    def num_recipes(self, obj):
        return obj.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following")
    search_fields = ("follower__username",)
