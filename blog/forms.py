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


class ChangNickNameForm(forms.Form):

    nickname_new = forms.CharField(label='新的昵称', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangNickNameForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError("用户没有登录")
        return self.data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError("新的昵称不能为空")
        return nickname_new


class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))
    verification_code = forms.CharField(label='验证码', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError("用户没有登录")
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定过邮箱')
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


class ChangePasswordForm(forms.Form):

    old_password = forms.CharField(label='当前的密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入当前密码'}))
    new_password = forms.CharField(label='新的的密码', min_length=6, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))
    new_password_again = forms.CharField(label='再输一次新密码', min_length=6, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请再次输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')

        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError("两次输入密码不一致")
        return self.cleaned_data

    def clean_old_password(self):
        # 验证旧的密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('当前密码错误')
        return old_password


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(label='用户名',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入绑定过的邮箱'}))
    verification_code = forms.CharField(label='验证码', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    new_password = forms.CharField(label='输入新密码', min_length=6, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱用户不存在')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        code = self.request.session.get('forgot_password_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError("验证码不正确")
        return verification_code
