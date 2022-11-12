from django.core.paginator import Paginator

RECENT_POSTS = 10


def get_paginator(queryset, request):
    paginator = Paginator(queryset, RECENT_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "page_obj": page_obj,
    }
