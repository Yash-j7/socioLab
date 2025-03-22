from itertools import chain
from  django . shortcuts  import  get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . models import  Followers, LikePost, Post, Profile
from django.db.models import Q
from django.http import JsonResponse
import json
import datetime
# import requests
import time
import random
# from agora_token_builder import RtcTokenBuilder
# from .models import RoomMember
import json
from django.views.decorators.csrf import csrf_exempt



def signup(request):
    try:
        if request.method == 'POST':
            print("here")
            username = request.POST['username']
            email = request.POST['email']       
            password = request.POST['password']
            print(username,email,password)
            my_user = User.objects.create_user(username,email,password)
            my_user.save()
            user_model = User.objects.get(username=username)
            profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            profile.save()
            if my_user is not None:
                login(request,my_user)
                return redirect('/')
            else:
                return redirect('/login')
    except Exception as e:
        print(e)
        invalid  = "user already exists"
        return render(request,'signup.html',{'invalid':invalid})
    return render(request,'signup.html')
def loginn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            invalid = "Invalid Credentials"
            return render(request,'login.html',{'invalid':invalid})
    return render(request,'loginn.html')

def logoutt(request):
    logout(request)
    return redirect("login")


def home(request):
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)
    post = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')

    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'id_user': request.user.id})

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'main.html', context)



def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


def likes(request, id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)

        like_filter = LikePost.objects.filter(post_id=id, username=username).first()

        if like_filter is None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1

        post.save()

        # Generate the URL for the current post's detail page
        print(post.id)

        # Redirect back to the post's detail page
        return redirect('/#'+id)
    
def explore(request):
    post=Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    context={
        'post':post,
        'profile':profile
        
    }
    return render(request, 'explore.html',context)


def profile(request, id_user):
    user_object = User.objects.get(username=id_user)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at')

    follower = request.user.username
    user = id_user

    follow_unfollow = 'Unfollow' if Followers.objects.filter(follower=follower, user=user).exists() else 'Follow'

    user_followers = Followers.objects.filter(user=id_user).count()
    user_following = Followers.objects.filter(follower=id_user).count()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': len(user_posts),
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    # **Process Profile Updates**
    if request.user.username == id_user:
        if request.method == 'POST':
            bio = request.POST.get('bio', user_profile.bio)  # Keep old bio if not changed
            location = request.POST.get('location', user_profile.location)  # Keep old location
            image = request.FILES.get('image') if request.FILES.get('image') else user_profile.profileimg

            # Update profile details
            user_profile.bio = bio.strip()
            user_profile.location = location.strip()
            user_profile.profileimg = image
            user_profile.save()

            return redirect('/profile/' + id_user)

    return render(request, 'profile.html', context)


def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()

    return redirect('/profile/'+ request.user.username)


def search_results(request):
    query = request.GET.get('q')

    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }
    return render(request, 'search_user.html', context)

def home_post(request,id):
    post=Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context={
        'post':post,
        'profile':profile
    }
    return render(request, 'main.html',context)



def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')