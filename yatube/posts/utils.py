from django.core.paginator import Paginator
from django.conf import settings


def pagination(request, posts):
    paginator = Paginator(posts, settings.MAX_POSTS)
    return paginator.get_page(request.GET.get('page'))
