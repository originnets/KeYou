from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models

from .models import Type, Posts, ReadNum, ReadDetail, LikeRecord, LikeCount, Comment
from markdown.widgets import AdminMarkdownWidget

# 自定义User
User = get_user_model()


# 在后台注册User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('avatar', 'nickname', 'email', )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('id', 'avatar', 'username', 'nickname', 'email', 'is_staff', 'is_active', 'is_superuser')


# 在后台注册Type
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')
    ordering = ('id',)


# 在后台注册Posts
@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownWidget()},
    }
    list_display = ('id', 'title', 'author', 'b_type', 'publish_time', 'modify_time', 'status')
    ordering = ('id',)


# 在后台注册ReadNum
@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ("read_num", "content_object")
    ordering = ("read_num", )


# 在后台注册ReadDetail
@admin.register(ReadDetail)
class ReadDetailAdmin(admin.ModelAdmin):
    list_display = ("date", "read_num", "content_object")
    ordering = ("read_num", )


# 在后台注册LikeCount
@admin.register(LikeCount)
class LikeCountAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "content_object", 'liked_num',)
    ordering = ("id",)  # 排序id为正序-id为倒序


# 在后台注册LikeRecord
@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "user", "liked_time")
    ordering = ("id",)


# 在后台注册Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'comment_text', 'comment_time', 'user', 'top_level', 'parent')