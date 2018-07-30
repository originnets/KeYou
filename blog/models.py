from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings

# Posts表的状态

STATUS = {0: u'草稿', 1: u'发布', }


# 自定义用户模型,对django添加nickname,avatar

class User(AbstractUser):
    nickname = models.CharField(max_length=20, default='', verbose_name='昵称')
    avatar = models.ImageField(upload_to="upload/avatar/%Y%m", default='upload/avatar/default.png', max_length=100, verbose_name='头像')

    class Meta(AbstractUser.Meta):
        pass

# 定义Blog主表


class Type(models.Model):
    type_name = models.CharField(max_length=30, verbose_name='类型名称')

    class Meta:
        verbose_name_plural = "博客类型"
        verbose_name = "博客类型"

    def __str__(self):
        return self.type_name


class Posts(models.Model):
    title = models.CharField(max_length=30, verbose_name='文章标题')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='作者')
    content = models.TextField(verbose_name='文章内容')
    b_type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='博客类型')
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    status = models.SmallIntegerField(default=1, choices=STATUS.items())

    class Meta:
        ordering = ['-publish_time']  # 排序

    def __str__(self):
        return self.title
