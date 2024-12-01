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
import os

from post.models import Post, Follow, Stream
from django.contrib.auth.models import User
from authy.models import Profile
from .forms import EditProfileForm, UserRegisterForm
from django.urls import resolve
from comment.models import Comment

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

    posts_with_media_info = []
    for post in posts:
        # Fetch the first picture or video from the post
        first_picture = post.pictures.first()
        media_info = None
        if first_picture:
            media_url = first_picture.image.url
            is_video = media_url.lower().endswith(('.mp4', '.webm'))
            media_info = {
                'url': media_url,
                'is_video': is_video
            }

        posts_with_media_info.append({
            'post': post,
            'media_info': media_info,
        })

        # posts_with_media_info.sort(key=lambda x: x['post'].posted, reverse=True)

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
        'posts_with_media_info': posts_with_media_info,

    }
    return render(request, 'profile.html', context)

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
        profile.skills = request.POST.get('skills')
        profile.role = request.POST.get('role')
        profile.interests = request.POST.get('interests')
        
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



# def register(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, 'Your account has been created successfully!')

#             # Automatically log in the user
#             new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
#             if new_user is not None:
#                 login(request, new_user)
#                 return redirect('index')
#             else:
#                 messages.error(request, "There was an issue logging you in. Please try logging in manually.")
#                 return redirect('sign-in')
#         else:
#             # Display form errors if validation fails
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field}: {error}")

#     else:
#         if request.user.is_authenticated:
#             return redirect('index')
#         form = UserRegisterForm()

#     context = {'form': form}
#     return render(request, 'sign-up.html', context)


from django.db import IntegrityError

def register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST, request.FILES)
        # profile_form = ProfileForm(request.POST)
        
        # if user_form.is_valid() and profile_form.is_valid():
        #     # Create the user
        #     user = user_form.save()
        if user_form.is_valid():
            # Create the user
            user = user_form.save()
            
            # Ensure the username is unique (it's automatically handled by Django)
            # Check if a Profile already exists for this user
            profile, created = Profile.objects.get_or_create(user=user)
            
            # If profile exists, update it, otherwise, set the fields from the form
            profile.first_name = user_form.cleaned_data.get('first_name', profile.first_name)
            profile.last_name = user_form.cleaned_data.get('last_name', profile.last_name)
            profile.bio = user_form.cleaned_data.get('bio', profile.bio)
            profile.location = user_form.cleaned_data.get('location', profile.location)
            profile.url = user_form.cleaned_data.get('url', profile.url)
            profile.skills = user_form.cleaned_data.get('skills', profile.skills)
            profile.interests = user_form.cleaned_data.get('interests', profile.interests)
            profile.role=user_form.cleaned_data.get('role', profile.role)

            # Set the profile image if provided
            if user_form.cleaned_data.get('image'):
                profile.image = user_form.cleaned_data.get('image')
                # if profile_form.cleaned_data.get('image'):
                # profile.image = user_form.cleaned_data.get('image')

            profile.save()  # Save the profile

            messages.success(request, 'Your account has been created successfully!')

            # Automatically log in the user
            new_user = authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password1'])
            if new_user is not None:
                login(request, new_user)
                return redirect('index')
            else:
                messages.error(request, "There was an issue logging you in. Please try logging in manually.")
                return redirect('sign-in')
        else:
            # Display form errors if validation fails
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # for field, errors in profile_form.errors.items():
            #     for error in errors:
            #         messages.error(request, f"{field}: {error}")

    else:
        if request.user.is_authenticated:
            return redirect('index')
        user_form = UserRegisterForm()
        # profile_form = ProfileForm()  # Create an empty form for profile

    context = {'user_form': user_form}
    # context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'sign-up.html', context)





def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("sign-in"))