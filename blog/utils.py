import datetime
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse


from .models import Type, Posts, ReadNum, ReadDetail
from django.conf import settings


# 定义返回字典
contexts = {}


# 获取分页数据
def get_posts_list_common_data(request, posts_list_datas):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(posts_list_datas, settings.EACH_PAGE_BLOG_NUMBER)
    pag_of_posts = paginator.get_page(page_num)
    currentr_page_num = pag_of_posts.number  # 获取当前页码
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + list \
        (range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    posts_datas = Posts.objects.dates('publish_time', 'month', order='DESC')  # 获取数据并排序
    posts_datas_dict = {}
    for posts_date in posts_datas:
        posts_count = Posts.objects.filter(status=1, publish_time__year=posts_date.year, publish_time__month=posts_date.month).count()
        posts_datas_dict[posts_date] = posts_count
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

        # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取posts分类对应博客数量
    posts_categorys = Type.objects.annotate(posts_count=Count('posts'))

    # 定义返回
    contexts['pag_of_posts'] = pag_of_posts
    contexts['page_range'] = page_range
    contexts['posts_categorys'] = posts_categorys
    contexts['posts_dates'] = posts_datas
    return contexts


# 阅读统计量
def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.id)
    if not request.COOKIES.get(key):
        # 总阅读数量 +1
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.id)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数量 +1
        date = timezone.now().date()
        readdetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.id, date=date)
        readdetail.read_num += 1
        readdetail.save()
    return key


# 获取最近7的的热门评论
def get_sevenday_hot_datas():
    today = timezone.now().date()
    data = today - datetime.timedelta(days=7)
    posts = Posts.objects.filter(read_details__date__lte=today, read_details__date__gt=data).values('id', 'title').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
    return posts[:5]


# 定义成功or失败的返回
def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

