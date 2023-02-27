from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like


def index(request) :
    posts = Post.objects.order_by('-date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/index.html', {
        'page_obj': page_obj,
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    

def new_post(request):
    if request.method == 'POST':
        content = request.POST['content']
        post = Post(author=request.user, content=content)
        post.save()
        return HttpResponseRedirect(reverse(index))
    return HttpResponseRedirect(reverse(index))


def profile(request, user_id):
    user_profile = User.objects.get(pk=user_id)
    num_followers = Follow.objects.filter(follower=user_profile).count()
    num_following = Follow.objects.filter(following=user_profile).count()

    posts = Post.objects.filter(author=user_profile).order_by('-date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(following=request.user, follower=user_profile).exists()
    else:
        is_following = False


    return render(request, 'network/profile.html', {
        'user_profile': user_profile,
        'num_followers': num_followers,
        'num_following': num_following,
        'posts': posts,
        'is_following': is_following,
        'page_obj': page_obj,
    })


def follow(request):
    follow_user = request.POST['userfollow']
    user = User.objects.get(pk=request.user.id)
    follow_user_data = User.objects.get(username=follow_user)
    follow = Follow(following=user, follower=follow_user_data)
    follow.save()
    user_id = follow_user_data.id
    return HttpResponseRedirect(reverse('profile', args=(user_id,)))

def unfollow(request):
    follow_user = request.POST['userfollow']
    user = User.objects.get(pk=request.user.id)
    follow_user_data = User.objects.get(username=follow_user)
    follow = Follow.objects.get(following=user, follower=follow_user_data)
    follow.delete()
    user_id = follow_user_data.id
    return HttpResponseRedirect(reverse('profile', args=(user_id,)))


def following(request):
    user = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(following=user)
    posts = Post.objects.none()
    for follow in following:
        posts |= Post.objects.filter(author=follow.follower)
    posts = posts.order_by('-date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/following.html', {
        'page_obj': page_obj,
    })


def edit_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        post.content = data["content"]
        post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})
    

def like_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        message = 'unliked'
    else:
        post.likes.add(user)
        message = 'liked'
    likes_count = post.likes.count()
    return JsonResponse({'likes': likes_count, 'message': message})