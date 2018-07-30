from django.core.paginator import Paginator
from django.db.models import Count

from .models import Type, Posts
from django.conf import settings


# 定义返回字典
return_value = {}


# 获取分页数据
def get_posts_list_common_data(request, posts_list_datas):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(posts_list_datas, settings.EACH_PAGE_BLOG_NUMBER)
    pag_of_posts = paginator.get_page(page_num)
    currentr_page_num = pag_of_posts.number  # 获取当前页码
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + list \
        (range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    posts_datas = Posts.objects.dates('publish_time', 'month', order='DESC')  # 获取数据并排序

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
    return_value['pag_of_posts'] = pag_of_posts
    return_value['page_range'] = page_range
    return_value['posts_categorys'] = posts_categorys
    return_value['posts_dates'] = posts_datas
    return return_value
