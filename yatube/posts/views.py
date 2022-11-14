from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Post, Group
from .forms import PostForm
from .utils import get_page_obj


User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    context = {"page_obj": get_page_obj(post_list, request)}
    return render(request, "posts/index.html", context)


def posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        "group": group,
        "page_obj": get_page_obj(post_list, request),
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = profile.posts.all()
    context = {
        "profile": profile,
        "page_obj": get_page_obj(post_list, request),
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        "post": post,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    form = PostForm()
    return render(
        request,
        "posts/create_post.html",
        {"form": form},
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    template = "posts/create_post.html"
    context = {
        "form": form,
        "is_edit": True,
        "post": post,
    }
    return render(request, template, context)
