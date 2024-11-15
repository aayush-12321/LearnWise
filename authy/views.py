from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout


from post.models import Post, Follow, Stream
from django.contrib.auth.models import User
from authy.models import Profile
from .forms import EditProfileForm, UserRegisterForm
from django.urls import resolve
from comment.models import Comment

# def UserProfile(request, username):
#     Profile.objects.get_or_create(user=request.user)
#     user = get_object_or_404(User, username=username)
#     profile = Profile.objects.get(user=user)
#     url_name = resolve(request.path).url_name
#     posts = Post.objects.filter(user=user).order_by('-posted')

#     if url_name == 'profile':
#         posts = Post.objects.filter(user=user).order_by('-posted')
#     else:
#         posts = profile.favourite.all()
    
#     # Profile Stats
#     posts_count = Post.objects.filter(user=user).count()
#     following_count = Follow.objects.filter(follower=user).count()
#     followers_count = Follow.objects.filter(following=user).count()
#     # count_comment = Comment.objects.filter(post=posts).count()
#     follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

#     # pagination
#     paginator = Paginator(posts, 8)
#     page_number = request.GET.get('page')
#     posts_paginator = paginator.get_page(page_number)

#     context = {
#         'posts': posts,
#         'profile':profile,
#         'posts_count':posts_count,
#         'following_count':following_count,
#         'followers_count':followers_count,
#         'posts_paginator':posts_paginator,
#         'follow_status':follow_status,
#         # 'count_comment':count_comment,
#     }
#     return render(request, 'profile.html', context)


def UserProfile(request, username):
    # Get the profile user (the one whose profile is being viewed)
    profile_user = get_object_or_404(User, username=username)

    # Ensure the profile exists
    Profile.objects.get_or_create(user=profile_user)
    profile = Profile.objects.get(user=profile_user)

    # Determine which posts to display (profile posts or favorites)
    url_name = resolve(request.path).url_name
    if url_name == 'profile':
        posts = Post.objects.filter(user=profile_user).order_by('-posted')
    else:
        posts = profile.favourite.all()

    # Profile stats
    posts_count = posts.count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    followers_count = Follow.objects.filter(following=profile_user).count()
    follow_status = Follow.objects.filter(following=profile_user, follower=request.user).exists()

    # Pagination
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,  # The user whose profile is being viewed
        'profile': profile,           # Profile object for the viewed user
        'posts': posts,               # Posts to display
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
        'posts_paginator': posts_paginator,
        'follow_status': follow_status,
    }
    return render(request, 'profile.html', context)

# def EditProfile(request):
#     user = request.user.id
#     profile = Profile.objects.get(user__id=user)

#     if request.method == "POST":
#         form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
#         if form.is_valid():
#             profile.image = form.cleaned_data.get('image')
#             profile.first_name = form.cleaned_data.get('first_name')
#             profile.last_name = form.cleaned_data.get('last_name')
#             profile.location = form.cleaned_data.get('location')
#             profile.url = form.cleaned_data.get('url')
#             profile.bio = form.cleaned_data.get('bio')
#             profile.save()
#             return redirect('profile', profile.user.username)
#     else:
#         form = EditProfileForm(instance=request.user.profile)

#     context = {
#         'form':form,
#     }
#     return render(request, 'editprofile.html', context)


from django.contrib import messages
import os
def editProfile(request):
    profile = request.user.profile  # Retrieve the profile of the logged-in user

    if request.method == "POST":
        if len(request.FILES) != 0:
            if profile.image and len(profile.image.path) > 0:
                os.remove(profile.image.path)  # Remove the old image if it exists
            profile.image = request.FILES['picture']

        profile.first_name = request.POST.get('first_name')
        profile.last_name = request.POST.get('last_name')
        profile.bio = request.POST.get('bio')
        profile.location = request.POST.get('location')
        profile.url = request.POST.get('url')
        
        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile', profile.user.username)

    context = {
        'profile': profile
    }
    return render(request, 'editprofile.html', context)



def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))


def followers_followings_list(request, user_id, follow_type):
    # Get the user whose profile is being viewed
    user = get_object_or_404(User, id=user_id)

    if follow_type == 'followers':
        # Fetch all users who follow this user
        followers = user.followers.all().select_related('follower')
        follow_users = [follow.follower for follow in followers]
        title = f"Followers of {user.username}"
    elif follow_type == 'followings':
        # Fetch all users this user is following
        followings = user.following.all().select_related('following')
        follow_users = [follow.following for follow in followings]
        title = f"Followings of {user.username}"
    else:
        follow_users = []
        title = "Invalid follow type"

    context = {
        'user': user,  # User being viewed
        'follow_users': follow_users,  # List of followers or followings
        'title': title,  # Title for the page
    }
    return render(request, 'follow_list.html', context)



def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account has been created successfully!')

            # Automatically log in the user
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if new_user is not None:
                login(request, new_user)
                return redirect('index')
            else:
                messages.error(request, "There was an issue logging you in. Please try logging in manually.")
                return redirect('sign-in')
        else:
            # Display form errors if validation fails
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        if request.user.is_authenticated:
            return redirect('index')
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'sign-up.html', context)



def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("sign-in"))