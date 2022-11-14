from django.core.paginator import Paginator

RECENT_POSTS = 10


def get_page_obj(queryset, request):
    paginator = Paginator(queryset, RECENT_POSTS)
    page_obj = paginator.get_page(request.GET.get("page"))
    return page_obj
