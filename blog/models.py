from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.fields import exceptions
from django.contrib.contenttypes.fields import GenericRelation


from django.conf import settings

# Posts表的状态

STATUS = {0: u'草稿', 1: u'发布', }


# 自定义用户模型,对django添加nickname,avatar
class User(AbstractUser):
    nickname = models.CharField(max_length=20, default='', verbose_name='昵称')
    avatar = models.ImageField(upload_to="upload/avatar/%Y%m", default='upload/avatar/default.png', max_length=100, verbose_name='头像')

    class Meta(AbstractUser.Meta):
        pass


# 建立阅读模型
class ReadNum(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    read_num = models.IntegerField(default=0, verbose_name="阅读数量")

    class Meta:
        verbose_name = "阅读数量"
        verbose_name_plural = "阅读数量"


class ReadDetail(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    date = models.DateField(default=timezone.now)
    read_num = models.IntegerField(default=0, verbose_name="阅读数量")

    class Meta:
        verbose_name = "阅读详情"
        verbose_name_plural = "阅读详情"


class ReadNumExpandMethod():
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(self)
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.id)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0


# 建立Blog模型
class Type(models.Model):
    type_name = models.CharField(max_length=30, verbose_name='类型名称')

    class Meta:
        verbose_name_plural = "博客类型"
        verbose_name = "博客类型"

    def __str__(self):
        return self.type_name


class Posts(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=30, verbose_name='文章标题')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='作者')
    content = models.TextField(verbose_name='文章内容')
    b_type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='博客类型')
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    status = models.SmallIntegerField(default=1, choices=STATUS.items())
    read_details = GenericRelation(ReadDetail)

    class Meta:
        ordering = ['-publish_time']  # 排序

    def __str__(self):
        return self.title


# 建立评论模型
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.CASCADE)

    top_level = models.ForeignKey('self', null=True, related_name="top_level_comment", on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, related_name="rep_comment", on_delete=models.CASCADE)
    rep_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rep_list", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_text

    class Meta:
        ordering = ['comment_time']
        verbose_name = "评论"
        verbose_name_plural = "评论"


# 建立点赞模型
class LikeCount(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    liked_num = models.IntegerField(default=0)

    class Meta:
        verbose_name = "点赞计数"
        verbose_name_plural = "点赞计数"


class LikeRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    liked_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "点赞记录"
        verbose_name_plural = "点赞记录"