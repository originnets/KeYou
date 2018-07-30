from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import auth

from .models import Type, Posts
from .utils import get_posts_list_common_data

# 自定义User模型
User = get_user_model()

# 定义返回字典
return_value = {}


def index(request):
    posts_list_datas = Posts.objects.all()
    return_value = get_posts_list_common_data(request, posts_list_datas)
    return render(request, 'index.html', return_value)


def about(request):
    return render(request, 'about.html', )


def contact(request):
    return render(request, 'contact.html', )


def article(request):
    return render(request, 'article.html', )