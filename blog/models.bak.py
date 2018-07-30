from django.db import models
from django.contrib.auth.models import User

# 继承User重构User添加nickname, avatar


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, default='', verbose_name='昵称')
    avatar = models.ImageField(upload_to="upload/avatar/%Y%m", default='upload/avatar/default.png', max_length=100, verbose_name='头像')

    def __str__(self):
        return self.nickname


# 获取昵称
def get_nickname(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''


# 获取用户名或昵称
def get_nickname_or_user(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username


# 查看是否存在昵称
def has_nickname(self):
    return Profile.objects.filter(user=self).exists()


# 获取头像
def get_avatar(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.avatar
    else:
        return ''


# 添加进User对象中
User.get_nickname = get_nickname
User.get_nickname_or_user = get_nickname_or_user
User.has_nickname = has_nickname
User.get_avatar = get_avatar

