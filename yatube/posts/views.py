from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .utils import pagination
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    context = {
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    context = {
        'author': author,
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form = form.save(commit=False)
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, template, {'form': form, 'is_edit': True})
