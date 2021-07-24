from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_items_paginator(request, item, item_per_page):
    posts_list = item.posts.all()
    paginator = Paginator(posts_list, item_per_page)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return page


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.ELEMENTS_PAGINATOR)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/index.html", {"page": page})


def group_posts(request, slug):
    """Функция get_object_or_404 получает по заданным критериям
    объект из базы данных или возвращает сообщение об ошибке,
    если объект не найден.
    """
    group = get_object_or_404(Group, slug=slug)
    page = get_items_paginator(request, group, settings.ELEMENTS_PAGINATOR)
    return render(request, "posts/group.html", {"group": group, "page": page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page = get_items_paginator(request, author, settings.ELEMENTS_PAGINATOR)
    user = request.user
    following = user.is_authenticated and (
        Follow.objects.filter(user=user, author=author).exists()
    )
    user_client = request.user
    return render(
        request,
        "profile.html",
        {
            "author": author,
            "page": page,
            "following": following,
            "user_client": user_client
        }
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        "posts/post.html",
        {"author": author, "post": post, "comments": comments, "form": form}
    )


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
        return render(
            request,
            "users/new_post.html",
            {"form": form, "switch": "new"})
    form = PostForm()
    return render(
        request,
        "users/new_post.html",
        {"form": form, "switch": "new"})


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)

    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post", username=request.user.username,
                            post_id=post_id)

    return render(
        request, "users/new_post.html", {"form": form, "post": post},
    )


def page_not_found(request, exception=None):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(
            "post",
            post_id=post_id,
            username=username
        )
    return redirect("post", post_id=post_id, username=username)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.ELEMENTS_PAGINATOR)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.create(author=author, user=request.user)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect("profile", username=username)
