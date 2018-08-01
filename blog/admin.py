from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models

from .models import Type, Posts
from markdown.widgets import AdminMarkdownWidget

# 自定义User
User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('avatar', 'nickname', 'email', )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('avatar', 'username', 'nickname', 'email', 'is_staff', 'is_active', 'is_superuser')


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')
    ordering = ('id',)


@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownWidget()},
    }
    list_display = ('id', 'title', 'author', 'b_type', 'publish_time', 'modify_time', 'status')
    ordering = ('id',)
