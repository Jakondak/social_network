from django.contrib import admin

from .models import Group, Post, Follow, Comment

empty_value_display_constant = "-пусто-"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = empty_value_display_constant


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = empty_value_display_constant


@admin.register(Follow)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user",)
    empty_value_display = empty_value_display_constant


@admin.register(Comment)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")
    search_fields = ("text",)
    empty_value_display = empty_value_display_constant
