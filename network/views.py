from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post
from .forms import PostForm, UserForm


def index(request):
    
    # Making new posts
    if request.method == "POST":
        form = PostForm(request.POST)
        
        # Save to the database
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Your post has been published!")
            return HttpResponseRedirect(reverse("index"))
        
    # Load all posts in reverse chronological order
    posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()
    
    # Show only 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "form": PostForm(),
        "page_obj": page_obj
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
    
def profile(request, user_id):
    
    # Get the user
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        
        # Following functionality
        if "follow" in request.POST:
            
            user.followers.add(request.user)
            messages.success(request, f"You are now following {user.username.capitalize()}")
            return HttpResponseRedirect(reverse("profile", args=(user.id,)))
            
        # Unfollowing functionality
        elif "unfollow" in request.POST:
            
            user.followers.remove(request.user)
            messages.success(request, f"You are no longer following {user.username.capitalize()}")
            return HttpResponseRedirect(reverse("profile", args=(user.id,)))
    
    # Get user information
    following = user.following.all()
    followers = user.followers.all()
    
    # Get all posts in reverse chronological order
    posts = user.posts.all()
    posts = posts.order_by("-timestamp").all()
    
    # Show only 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        "no_of_following": len(following),
        "no_of_followers": len(followers),
        "page_obj": page_obj,
        "profile_user": user
    })

@login_required
def following(request):
    
    # Load all posts from users the current user follows in reverse chronological order 
    posts = Post.objects.filter(user__followers=request.user)
    posts = posts.order_by("-timestamp").all()
    
    # Show only 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

@csrf_exempt
@login_required
def edit(request, post_id):
    
    # Query for requested post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post content
    if request.method == "GET":
        return JsonResponse(post.serialize())
    
    # Like and edit post
    elif request.method == "PUT":
        data = json.loads(request.body)
        
        if data.get("liked_by") is not None:
            user = data["liked_by"]
            user = User.objects.get(username=user)
            if user in post.likes.all():
                post.likes.remove(user)
                return HttpResponse(status=204)
            else:
                post.likes.add(user)
                return HttpResponse(status=204)
            
        if data.get("content") is not None:
            if post.user == request.user:
                post.content = data["content"]
                #post.content = new_content
                post.save()
                return HttpResponse(status=204)
                #return JsonResponse({"new_content": new_content}, status=204)
            else:
                return JsonResponse({"error": "You cannot edit other user's post."}, status=400)
        
    # Other request types are not accepted
    else:
        return JsonResponse({"error": "GET or PUT required."}, status=400)