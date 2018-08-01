from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.db.models import Count
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
    posts_list_datas = Posts.objects.filter(status=1).all()
    return_value = get_posts_list_common_data(request, posts_list_datas)
    return render(request, 'index.html', return_value)


def article(request, aid):
        posts_detail_data = get_object_or_404(Posts, status=1, id=aid)
        previous_posts = Posts.objects.filter(status=1, publish_time__gt=posts_detail_data.publish_time).last()
        next_posts = Posts.objects.filter(status=1, publish_time__lt=posts_detail_data.publish_time).first()
        posts_categorys = Type.objects.annotate(posts_count=Count('posts'))
        posts_datas = Posts.objects.dates('publish_time', 'month', order='DESC')
        posts_datas_dict = {}
        for posts_date in posts_datas:
            posts_count = Posts.objects.filter(status=1, publish_time__year=posts_date.year,
                                               publish_time__month=posts_date.month).count()
            posts_datas_dict[posts_date] = posts_count

        return_value['posts_detail_data'] = posts_detail_data
        return_value['previous_posts'] = previous_posts
        return_value['next_posts'] = next_posts
        return_value['posts_categorys'] = posts_categorys
        return_value['posts_datas'] = posts_datas_dict
        return render(request, 'article.html', return_value,)


def posts_type(request, tid):
    posts_list_datas = Posts.objects.filter(status=1, b_type__id=tid)
    posts_category = Type.objects.filter(id=tid).first()
    return_value = get_posts_list_common_data(request, posts_list_datas)
    return_value['posts_category'] = posts_category
    return render(request, 'posts_type.html', return_value,)


def posts_time(request, year, month):
    posts_list_datas = Posts.objects.filter(status=1, publish_time__year=year, publish_time__month=month)
    return_value = get_posts_list_common_data(request, posts_list_datas)
    return_value['posts_time'] = '%s年%s月' % (year, month)
    return render(request, "posts_time.html", return_value, )


def about(request):
    return render(request, 'about.html', )


def contact(request):
    return render(request, 'contact.html', )
