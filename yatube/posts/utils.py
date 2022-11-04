from django.core.paginator import Paginator

from yatube.settings import MAX_POSTS


def pagination(request, posts):
    paginator = Paginator(posts, MAX_POSTS)
    return paginator.get_page(request.GET.get('page'))
