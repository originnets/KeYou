from django import forms
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from ckeditor.widgets import CKEditorWidget
from .models import Comment


User = get_user_model()


class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    comment_text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor',), error_messages={'required': "评论内容不能为空"})
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'reply_comment_id'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登陆
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        # 评论对象验证
        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        try:
            model_class = ContentType.objects.get(model=content_type).model_class()
            model_obj = model_class.objects.get(id=object_id)
            self.cleaned_data['content_obj'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:
            raise forms.ValidationError('回复出错')
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(id=reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(id=reply_comment_id)
        else:
            raise forms.ValidationError('回复出错')
        return reply_comment_id


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label="用户名或邮箱", required=True, widget=forms.TextInput(attrs={'class': "form-control", "placeholder": "请输入用户名或邮箱"}),)
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={'class': "form-control", "placeholder": "请输入密码"}),)

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('有户名密码错误')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=30, min_length=3, required=True, widget=forms.TextInput(attrs={'class': "form-control", "placeholder": "请输入用户名"}),)
    email = forms.EmailField(label="邮箱",  required=True, widget=forms.TextInput(attrs={'class': "form-control", "placeholder": "请输入邮箱"}),)
    verification_code = forms.CharField(label='验证码', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    password = forms.CharField(label="密码", min_length=6, widget=forms.PasswordInput(attrs={'class': "form-control", "placeholder": "请输入密码"}),)
    password_again = forms.CharField(label="密码", min_length=6, widget=forms.PasswordInput(attrs={'class': "form-control", "placeholder": "请输入一次密码"}),)

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次密码输入不一致')
        return password_again

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code