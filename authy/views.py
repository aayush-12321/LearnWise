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
from authy.models import Profile,Rating
from .forms import EditProfileForm, UserRegisterForm
from django.urls import resolve
from comment.models import Comment

from django.db.models import Avg
from django.db import models  # Ensure you add this import
from .forms import RatingForm
from django.http import JsonResponse
from django.db.models import Q
from .models import Rating, User
from .forms import RatingForm
from django.db.models import Count

@login_required
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

    # Calculate the average rating for the profile user
    avg_rating = Rating.objects.filter(rated_user=profile_user).aggregate(Avg('rating'))['rating__avg']
    avg_rating = avg_rating or 0  # Default to 0 if no ratings
    avg_rating_int = int(avg_rating)  # Full stars
    half_star = (avg_rating - avg_rating_int) >= 0.5  # Check if it's a half star
    stars_range = range(1, 6)  # Assuming a 5-star rating system
    next_full_star = avg_rating_int + 1 if half_star else avg_rating_int
    total_ratings = Rating.objects.filter(rated_user=profile_user).count()


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

    paginator = Paginator(posts_with_media_info, 6)
    page_number = request.GET.get('page')
    posts_with_media_info = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,  # The user whose profile is being viewed
        'profile': profile,           # Profile object for the viewed user
        # 'posts': posts_paginator,               # Posts to display
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
        # 'posts_paginator': posts_paginator,
        'follow_status': follow_status,
        'posts_with_media_info': posts_with_media_info,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,  # Full stars
        'half_star': half_star,            # Whether to show a half star
        'stars_range': stars_range,        # Range for stars
        'next_full_star': next_full_star,
        'total_ratings': total_ratings,

    }
    return render(request, 'profile.html', context)

@login_required
def editProfile(request):
    profile = request.user.profile  # Retrieve the profile of the logged-in user

    if request.method == "POST":
        if len(request.FILES) != 0:
            if profile.image and len(profile.image.path) > 0 and profile.image!="default.png":
                os.remove(profile.image.path)  # Remove the old image if it exists
            profile.image = request.FILES['picture']

        profile.first_name = request.POST.get('first_name')
        profile.last_name = request.POST.get('last_name')
        profile.bio = request.POST.get('bio')
        # profile.location = request.POST.get('location')
        manual_location = request.POST.get('manual_location')
        map_location = request.POST.get('location')
        profile.location = manual_location if manual_location else map_location
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


@login_required
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

@login_required
def followers_followings_list(request, user_id, follow_type):
    # Get the user whose profile is being viewed
    user = get_object_or_404(User, id=user_id)

    # Determine the display name
    display_name = f"{user.profile.first_name.title()} {user.profile.last_name.title()}" if user.profile.first_name and user.profile.last_name else user.username

    if follow_type == 'followers':
        # Fetch all users who follow this user
        followers = user.followers.all().select_related('follower')
        follow_users = [follow.follower for follow in followers]
        title = f"Followers of {display_name}"
    elif follow_type == 'followings':
        # Fetch all users this user is following
        followings = user.following.all().select_related('following')
        follow_users = [follow.following for follow in followings]
        # title = f"Followings of {user.username}"
        title = f"Followings of {display_name}"
    else:
        follow_users = []
        title = "Invalid follow type"

    paginator = Paginator(follow_users, 4)
    page_number = request.GET.get('page')
    follow_paginator = paginator.get_page(page_number)

    context = {
        'user': user,  # User being viewed
        # 'follow_users': follow_users,  # List of followers or followings
        'follow_users': follow_paginator,  # List of followers or followings
        'title': title,  # Title for the page
    }
    return render(request, 'follow_list.html', context)

@login_required
def rate_user(request, user_id):
    rated_user = get_object_or_404(User, id=user_id)

    # Prevent users from rating their own profile
    if rated_user == request.user:
        return redirect('profile', username=request.user.username)

    message = None
    existing_rating = None

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rate_type = form.cleaned_data['rate_type']
            existing_rating = Rating.objects.filter(
                reviewer=request.user, rated_user=rated_user, rate_type=rate_type
            ).first()

            if existing_rating:
                # Update the existing rating for the same type
                existing_rating.rating = form.cleaned_data['rating']
                existing_rating.review = form.cleaned_data['review']
                existing_rating.save()
                message = f"Your {rate_type} rating has been updated."
            else:
                # Create a new rating for the specified type
                new_rating = form.save(commit=False)
                new_rating.reviewer = request.user
                new_rating.rated_user = rated_user
                new_rating.save()
                message = f"You have successfully rated {rated_user.username} for {rate_type}."

            return redirect('user_ratings', rated_user_id=rated_user.id)
    else:
        # Fetch the existing rating for pre-filling (if any)
        existing_rating = Rating.objects.filter(
            reviewer=request.user, rated_user=rated_user
        ).first()
        form = RatingForm(instance=existing_rating)

    return render(request, 'rate_user.html', {
        'form': form,
        'rated_user': rated_user,
        'message': message,
        'existing_rating': existing_rating,
    })

# def user_ratings(request, rated_user_id):
#     rated_user = get_object_or_404(User, id=rated_user_id)
#     rate_type_filter = request.GET.get('rate_type', '')  # Fetch filter value from GET
#     ratings = Rating.objects.filter(rated_user=rated_user)
    
#     rating_counts = Rating.objects.filter(rated_user=rated_user).values('rate_type').annotate(count=Count('id'))
#     rating_type_counts = {item['rate_type']: item['count'] for item in rating_counts}
    

#     # Apply filter only if a type is selected
#     if rate_type_filter:
#         ratings = ratings.filter(rate_type=rate_type_filter)

#     avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']

#     # If the user has rated this profile, show their ratings at the top
#     user_ratings = None
#     if request.user.is_authenticated:
#         # Fetch the ratings posted by the current user (both learning and mentorship if they exist)
#         user_ratings = ratings.filter(reviewer=request.user)
#         if user_ratings.exists():
#             # Exclude these user ratings from the main ratings list
#             ratings = ratings.exclude(id__in=user_ratings.values_list('id', flat=True))
#             # Add the user's ratings at the top
#             ratings = list(user_ratings) + list(ratings)

#     return render(request, 'user_ratings.html', {
#         'rated_user': rated_user,
#         'ratings': ratings,
#         'avg_rating': avg_rating,
#         'rate_type_filter': rate_type_filter,
#         'rating_type_counts': rating_type_counts,
#     })

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
@login_required
def user_ratings(request, rated_user_id):
    rated_user = get_object_or_404(User, id=rated_user_id)
    rate_type_filter = request.GET.get('rate_type', '')  # Fetch filter value from GET
    ratings = Rating.objects.filter(rated_user=rated_user)
    
    rating_counts = Rating.objects.filter(rated_user=rated_user).values('rate_type').annotate(count=Count('id'))
    rating_type_counts = {item['rate_type']: item['count'] for item in rating_counts}
    
    # Apply filter only if a type is selected
    if rate_type_filter:
        ratings = ratings.filter(rate_type=rate_type_filter)

    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']

    # If the user has rated this profile, show their ratings at the top
    user_ratings = None
    if request.user.is_authenticated:
        # Fetch the ratings posted by the current user (both learning and mentorship if they exist)
        user_ratings = ratings.filter(reviewer=request.user)
        if user_ratings.exists():
            # Exclude these user ratings from the main ratings list
            ratings = ratings.exclude(id__in=user_ratings.values_list('id', flat=True))
            # Add the user's ratings at the top
            ratings = list(user_ratings) + list(ratings)

    # Pagination setup
    paginator = Paginator(ratings, 6)  # Show 10 ratings per page
    page = request.GET.get('page')

    try:
        ratings_page = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        ratings_page = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results.
        ratings_page = paginator.page(paginator.num_pages)

    return render(request, 'user_ratings.html', {
        'rated_user': rated_user,
        'ratings': ratings_page,
        'avg_rating': avg_rating,
        'rate_type_filter': rate_type_filter,
        'rating_type_counts': rating_type_counts,
    })

@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    if rating.reviewer != request.user:
        return JsonResponse({'success': False, 'message': 'You cannot delete this rating.'}, status=403)

    rated_user_id = rating.rated_user.id  # Save the rated user's ID before deletion
    rating.delete()

    # Redirect to the user_ratings view with the rated user's ID
    return redirect(reverse('user_ratings', args=[rated_user_id]))



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
            # profile.location = user_form.cleaned_data.get('location', profile.location)
            profile.url = user_form.cleaned_data.get('url', profile.url)
            profile.skills = user_form.cleaned_data.get('skills', profile.skills)
            profile.interests = user_form.cleaned_data.get('interests', profile.interests)
            profile.role=user_form.cleaned_data.get('role', profile.role)

            # Set the profile image if provided
            if user_form.cleaned_data.get('image'):
                profile.image = user_form.cleaned_data.get('image')
                # if profile_form.cleaned_data.get('image'):
                # profile.image = user_form.cleaned_data.get('image')

            # Use manual location if provided, otherwise use map location
            manual_location = user_form.cleaned_data.get('manual_location')
            if manual_location:
                profile.location = manual_location
            else:
                profile.location = user_form.cleaned_data.get('location',profile.location)


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