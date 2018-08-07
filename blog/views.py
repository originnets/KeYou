from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import ObjectDoesNotExist
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import auth
import string, random, time
from django.core.mail import send_mail

from .models import Type, Posts, LikeRecord, LikeCount, Comment
from .forms import CommentForm, LoginForm, RegForm, ChangNickNameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .utils import get_posts_list_common_data, get_sevenday_hot_datas, read_statistics_once_read, ErrorResponse, SuccessResponse

# 自定义User模型
User = get_user_model()

# 定义返回字典
contexts = {}


def index(request):

    posts_list_datas = Posts.objects.filter(status=1).all()
    contexts = get_posts_list_common_data(request, posts_list_datas)
    return render(request, 'index.html', contexts)


def article(request, aid):
        posts_detail_data = get_object_or_404(Posts, status=1, id=aid)
        previous_posts = Posts.objects.filter(status=1, publish_time__gt=posts_detail_data.publish_time).last()
        next_posts = Posts.objects.filter(status=1, publish_time__lt=posts_detail_data.publish_time).first()
        posts_categorys = Type.objects.annotate(posts_count=Count('posts'))
        read_cookie_key = read_statistics_once_read(request, posts_detail_data)
        posts_datas = Posts.objects.dates('publish_time', 'month', order='DESC')
        posts_datas_dict = {}
        for posts_date in posts_datas:
            posts_count = Posts.objects.filter(status=1, publish_time__year=posts_date.year,
                                               publish_time__month=posts_date.month).count()
            posts_datas_dict[posts_date] = posts_count

        hot_posts_for_seven_days = cache.get('hot_posts_for_seven_days')
        if hot_posts_for_seven_days is None:
            hot_posts_for_seven_days = get_sevenday_hot_datas()
            cache.set('hot_posts_for_seven_days', hot_posts_for_seven_days, 3600)
            contexts['posts_detail_data'] = posts_detail_data
            contexts['previous_posts'] = previous_posts
            contexts['next_posts'] = next_posts
            contexts['posts_categorys'] = posts_categorys
            contexts['posts_datas'] = posts_datas_dict
            contexts['sevenday_hot_datas'] = hot_posts_for_seven_days
        response = render(request, 'article.html', contexts,)
        response.set_cookie(read_cookie_key, 'ture')
        return response


def posts_type(request, tid):
    posts_list_datas = Posts.objects.filter(status=1, b_type__id=tid)
    posts_category = Type.objects.filter(id=tid).first()
    contexts = get_posts_list_common_data(request, posts_list_datas)
    contexts['posts_category'] = posts_category
    return render(request, 'posts_type.html', contexts,)


def posts_time(request, year, month):
    posts_list_datas = Posts.objects.filter(status=1, publish_time__year=year, publish_time__month=month)
    contexts = get_posts_list_common_data(request, posts_list_datas)
    contexts['posts_time'] = '%s年%s月' % (year, month)
    return render(request, "posts_time.html", contexts, )


def like_change(request):
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(400, '你尚未登录')
    content_type = request.POST.get('content_type')
    object_id = int(request.POST.get('object_id'))

    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(id=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, '该对象不存在')

    if request.POST.get('is_like') == 'true':
        # 要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            # 未点赞过，进行点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return ErrorResponse(402, '已点赞过')
    else:
        # 要取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数减1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(403, 'data error')
        else:
            # 没有点赞过，不能取消
            return ErrorResponse(404, 'y没有点赞过')


def update_comment(request):
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}

    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.comment_text = comment_form.cleaned_data['comment_text']
        comment.content_object = comment_form.cleaned_data['content_obj']

        parent = comment_form.cleaned_data['parent']
        if parent is not None:
            comment.top_level = parent.top_level if parent.top_level is not None else parent
            comment.parent = parent
            comment.rep_to = parent.user
        comment.save()

        # 返回状态
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        # data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['comment_time'] = comment.comment_time.timestamp()
        data['comment_text'] = comment.comment_text
        if parent is not None:
            data['reply_to'] = comment.rep_to.username
        else:
            data['reply_to'] = ''
        data['id'] = comment.id
        data['top_level'] = comment.top_level.id if comment.top_level is not None else ''
        # return redirect(referer)
    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)


def about(request):
    return render(request, 'about.html', )


def contact(request):
    return render(request, 'contact.html', )


def login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)  # 登陆
            return redirect(request.GET.get('from', reverse('index')))


def register(request):
    if request.method == "POST":
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            request.user.email = email
            password = reg_form.cleaned_data['password']
            # 创建用户
            new_user = User.objects.create_user(username, email, password)
            new_user.save()
            # 清除session
            del request.session['register_code']
            # 登陆用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == "POST":
        form = ChangNickNameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = User.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangNickNameForm()

    contexts = {}
    contexts['form'] = form
    contexts['page_title'] = "修改昵称"
    contexts['form_title'] = "修改昵称"
    contexts['submit_text'] = "修改"
    contexts['return_back_url'] = redirect_to
    return render(request, 'base/form.html', contexts)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == "POST":
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    contexts['form'] = form
    contexts['page_title'] = "绑定邮箱"
    contexts['form_title'] = "绑定邮箱"
    contexts['submit_text'] = "绑定"
    contexts['return_back_url'] = redirect_to
    return render(request, 'bind_email.html', contexts)


def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now
            # 发送邮件
            send_mail(
                '绑定邮箱',
                '你好：%s \n 你的验证码为: %s' % (email, code),
                '1421863463@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def change_password(request):
    redirect_to = reverse('home')
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            #old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password_again']
            user.set_password(new_password)
            user.save()
            request.user.save
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    contexts['form'] = form
    contexts['page_title'] = "修改密码"
    contexts['form_title'] = "修改密码"
    contexts['submit_text'] = "修改"
    contexts['return_back_url'] = redirect_to
    return render(request, 'base/form.html', contexts)


def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    contexts['form'] = form
    contexts['page_title'] = "重置密码"
    contexts['form_title'] = "重置密码"
    contexts['submit_text'] = "重置"
    contexts['return_back_url'] = redirect_to
    return render(request, 'forgot_password.html', contexts)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('index')))

