from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse

from post.models import Post, Tag, Follow, Stream
from django.contrib.auth.models import User
from authy.models import Profile
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator
from post.models import PostImage
from django.db.models import Q
from django.utils import timezone

@login_required
def index(request):
    user = request.user
    following_ids = set(Follow.objects.filter(follower=user).values_list('following', flat=True))
    mutual_follow_ids = set(Follow.objects.filter(following=user).values_list('follower', flat=True)).intersection(following_ids)

    # Fetch posts
    own_posts = Post.objects.filter(user=user)
    following_posts = Post.objects.filter(user__in=following_ids)
    mutual_posts = Post.objects.filter(user__in=mutual_follow_ids)
    other_posts = Post.objects.exclude(user__in=following_ids).exclude(user=user)
    all_posts = own_posts | following_posts | mutual_posts | other_posts

    # Scoring posts
    scored_posts = []
    for post in all_posts:
        # Set scoring parameters based on post type
        if post.user.id in following_ids:
            # Following user's post: Highest priority
            relationship_multiplier = 2.8  # Higher weight for following users
            like_weight = 2.8
            comment_weight = 2.3
            recency_decay = 1.01  # Slower decay rate
        elif post.user == user:
            # User's own post: Slightly lower priority
            relationship_multiplier = 2.0
            like_weight = 2.0
            comment_weight = 1.8
            recency_decay = 1.2
        elif post.user.id in mutual_follow_ids:
            # Mutual follower's post: Lower priority
            relationship_multiplier = 1.5
            like_weight = 1.8
            comment_weight = 1.5
            recency_decay = 1.3
        else:
            # Other user's post: Lowest priority
            relationship_multiplier = 1.0
            like_weight = 1.5
            comment_weight = 1.2
            recency_decay = 1.4

        # Calculate score based on likes, comments, and recency
        likes = post.likes
        comments_count = post.comment.count()  # Assuming Post has a related name `comment` for comments

        days_since_post = (timezone.now().date() - post.posted).days
        # print(days_since_post)
        recency_factor = recency_decay ** days_since_post

        # Score formula
        score = ((likes + 1) * like_weight + (comments_count + 1) * comment_weight) / recency_factor
        score *= relationship_multiplier
        scored_posts.append((post, score))

    # Sort posts by score (descending order)
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    sorted_posts = [post for post, _ in scored_posts]

    # Identify liked and saved posts
    liked_post_ids = Post.objects.filter(likers=user).values_list('id', flat=True)
    saved_post_ids = Post.objects.filter(savers=user).values_list('id', flat=True)

    # Handle search query if present
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query))
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

    # Suggestions based on mutual friends
    followings = set(Follow.objects.filter(follower=request.user).values_list('following', flat=True))
    potential_suggestions = User.objects.exclude(pk__in=followings).exclude(pk=request.user.pk)
    suggestions_with_mutuals = []
    for suggested_user in potential_suggestions:
        mutual_friends_count = Follow.objects.filter(following=suggested_user, follower__in=followings).count()
        suggestions_with_mutuals.append((suggested_user, mutual_friends_count))

    sorted_suggestions = sorted(suggestions_with_mutuals, key=lambda x: x[1], reverse=True)[0:5]
    suggestions = [user for user, _ in sorted_suggestions]

        
    # print(media_info)

    # Paginate sorted posts
    paginator = Paginator(sorted_posts, 5)
    page_number = request.GET.get('page')
    sorted_posts = paginator.get_page(page_number)

    # Prepare context and render template
    context = {
        'post_items': sorted_posts,
        'liked_post_ids': list(liked_post_ids),
        'saved_post_ids': list(saved_post_ids),
        'suggestions': suggestions,
        # 'media_info': media_info,
    }
    return render(request, 'index.html', context)

#before trying for file size limit
# @login_required
# def NewPost(request):
#     # Define the maximum size in bytes (100 MB = 100 * 1024 * 1024)
#     MAX_SIZE = 50 * 1024 * 1024

#     if request.method == 'POST':
#         caption = request.POST.get('caption', '')
#         tags_form = request.POST.get('tags', '')
#         pictures = request.FILES.getlist('pictures')

#         if caption or pictures:
#             post = Post.objects.create(
#                 user=request.user,
#                 caption=caption,
#             )
#             # Handle tags
#             if tags_form:
#                 tag_list = tags_form.split(',')
#                 for tag in tag_list:
#                     t, created = Tag.objects.get_or_create(title=tag.strip())
#                     post.tags.add(t)

#             # Save pictures
#             for picture in pictures:
#                 if picture.size > MAX_SIZE:
#                     messages.error(request, 'Size of a file should be less than 100 MB.')

#                 else:
#                     PostImage.objects.create(post=post, image=picture)

#             messages.success(request, 'Your post has been created!')
#             return redirect('profile', request.user.username)
#         else:
#             messages.error(request, 'Please provide a caption or pictures.')

#     return render(request, 'newpost.html')

@login_required
def NewPost(request):
    # Define the maximum size in bytes (50 MB = 50 * 1024 * 1024)
    MAX_SIZE = 50 * 1024 * 1024
    MAX_FILES = 20  # Maximum number of files
    error_message = ''  # Initialize error_message
    success_message = ''  # Initialize success_message

    if request.method == 'POST':
        caption = request.POST.get('caption', '')
        tags_form = request.POST.get('tags', '')
        pictures = request.FILES.getlist('pictures')

        if len(pictures) > MAX_FILES:
            error_message = f"You can only upload a maximum of {MAX_FILES} files. Please reduce the number of files."
            return render(request, 'newpost.html', {'error_message': error_message})  # Return with error message

        # Check if any file exceeds the size limit
        oversized_pictures = [picture.name for picture in pictures if picture.size > MAX_SIZE]
        if oversized_pictures:
            error_message = f"The following files exceed the 50 MB limit: {', '.join(oversized_pictures)}. Post not created."
            return render(request, 'newpost.html', {'error_message': error_message})  # Stop execution and return to form

        if caption or pictures:
            post = Post.objects.create(
                user=request.user,
                caption=caption,
            )
            # Handle tags
            if tags_form:
                tag_list = tags_form.split(',')
                for tag in tag_list:
                    t, created = Tag.objects.get_or_create(title=tag.strip())
                    post.tags.add(t)

            # Save valid pictures
            for picture in pictures:
                PostImage.objects.create(post=post, image=picture)

            success_message = 'Your post has been created!'
            return redirect('profile', request.user.username)

        else:
            error_message = 'Please provide a caption or pictures.'

    return render(request, 'newpost.html', {'error_message': error_message, 'success_message': success_message})

@login_required
def PostDetail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    user = request.user
    # print(user)

    # Identify liked and saved posts
    liked_post_ids = Post.objects.filter(likers=user).values_list('id', flat=True)
    saved_post_ids = Post.objects.filter(savers=user).values_list('id', flat=True)

    # Comments
    # comments = Comment.objects.filter(post=post).order_by('-date')

    role_filter = request.GET.get('role', '')  # Role filter (Mentor/Learner)
    if not role_filter in ['Mentor', 'Learner']:
        comments = Comment.objects.filter(post=post).order_by('-date')
    else:
        comments = Comment.objects.filter(post=post).order_by('-date')
        comments = comments.filter(user__profile__role=role_filter).order_by('-date')
    
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    comments_paginator = paginator.get_page(page_number)

    # Process media info for the post
    media_info = []
    for picture in post.pictures.all():
        media_url = picture.image.url
        is_video = media_url.lower().endswith(('.mp4', '.webm'))
        media_info.append({
            'url': media_url,
            'is_video': is_video
        })

    if request.method == "POST":
        form = NewCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
    else:
        form = NewCommentForm()

    context = {
        'post': post,
        'form': form,
        # 'comments': comments,
        'comments': comments_paginator,
        'role_filter': role_filter,
        'liked_post_ids': list(liked_post_ids),
        'saved_post_ids': list(saved_post_ids),
        'media_info': media_info,  # Add media info to context
    }

    return render(request, 'postdetail.html', context)

# @login_required
# def Tags(request, tag_slug):
#     tag = get_object_or_404(Tag, slug=tag_slug)
#     posts = Post.objects.filter(tags=tag).order_by('-posted')

#     posts_with_media_info = []
#     for post in posts:
#         # Fetch the first picture or video from the post
#         first_picture = post.pictures.first()
#         media_info = None
#         if first_picture:
#             media_url = first_picture.image.url
#             is_video = media_url.lower().endswith(('.mp4', '.webm'))
#             media_info = {
#                 'url': media_url,
#                 'is_video': is_video
#             }

#         posts_with_media_info.append({
#             'post': post,
#             'media_info': media_info,
#         })

#     context = {
#         'posts_with_media_info': posts_with_media_info,
#         'tag': tag,
#     }
#     return render(request, 'tag.html', context)


@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

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

    paginator = Paginator(posts_with_media_info, 6)
    page_number = request.GET.get('page')
    tags_paginator = paginator.get_page(page_number)

    context = {
        'posts_with_media_info': tags_paginator,
        'tag': tag,
    }
    return render(request, 'tag.html', context)

@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)

    
    if post.likers.filter(id=user.id).exists():
        post.likers.remove(user)
        post.likes -= 1
    else:
        post.likers.add(user)
        post.likes += 1

    post.save()
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


@login_required
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if post in profile.favourite.all():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)

    post.savers.add(user) if user not in post.savers.all() else post.savers.remove(user)
    post.save()
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

@login_required
def post_likers(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Get the usernames of the likers
    likers = post.likers.all()  # Assuming likers is a ManyToManyField

    paginator = Paginator(likers, 4)
    page_number = request.GET.get('page')
    likers_paginator = paginator.get_page(page_number)

    context = {
        'post': post,
        # 'likers': likers,
        'likers': likers_paginator,
        
    }
    return render(request, 'likers.html', context)
    
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)  # Ensure the user can only edit their own posts
    
    # Define the maximum size in bytes (50 MB = 50 * 1024 * 1024)
    MAX_SIZE = 50 * 1024 * 1024
    MAX_FILES = 20  # Maximum number of files

    if request.method == 'POST':
        # Retrieve form data
        caption = request.POST.get('caption', '').strip()
        tags_form = request.POST.get('tags', '').strip()
        pictures = request.FILES.getlist('pictures')
        remove_images = request.POST.getlist('remove_images')

        # Calculate the total number of files after considering existing and new files
        current_picture_count = post.pictures.exclude(id__in=remove_images).count()  # Pictures not marked for removal
        new_picture_count = len(pictures)  # Number of new pictures being uploaded
        total_picture_count = current_picture_count + new_picture_count

        # Check if the number of files exceeds the limit
        if total_picture_count > MAX_FILES:
            error_message = f"You can only upload a maximum of {MAX_FILES} files. Please reduce the number of files."
            return render(request, 'editpost.html', {'post': post, 'error_message': error_message})  # Return with error message

        # Check if any file exceeds the size limit
        oversized_pictures = [picture.name for picture in pictures if picture.size > MAX_SIZE]
        if oversized_pictures:
            error_message = f"The following files exceed the 50 MB limit: {', '.join(oversized_pictures)}. Post not updated."
            return render(request, 'editpost.html', {'post': post, 'error_message': error_message})  # Return with error message

        # Check if removing caption without picture or removing picture without caption
        has_existing_images = post.pictures.exclude(id__in=remove_images).exists()  # Remaining images after removal
        is_caption_empty = not caption
        is_picture_empty = not pictures and not has_existing_images

        if is_caption_empty and not post.pictures.exists():
            error_message = "You cannot remove the caption unless a picture is provided."
            return render(request, 'editpost.html', {'post': post, 'error_message': error_message})

        if is_picture_empty and not caption:
            error_message = "You cannot remove the picture unless a caption is provided."
            return render(request, 'editpost.html', {'post': post, 'error_message': error_message})

        # Update the post's caption (allow blank)
        post.caption = caption

        # Handle tags
        if tags_form:
            post.tags.clear()  # Remove all existing tags
            tag_list = tags_form.split(',')
            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag.strip())
                post.tags.add(t)
        elif not tags_form:
            post.tags.clear()  # Remove all tags if no tags are provided

        # Handle image removal
        for image_id in remove_images:
            post.pictures.filter(id=image_id).delete()

        # Handle new pictures
        if pictures:
            for picture in pictures:
                PostImage.objects.create(post=post, image=picture)

        post.save()  # Save changes
        success_message = "Post updated successfully!"
        return redirect('post-details', post.id)

    return render(request, 'editpost.html', {'post': post})


# @login_required
# def edit_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id, user=request.user)  # Ensure the user can only edit their own posts
#     if request.method == 'POST':
#         # Retrieve form data
#         caption = request.POST.get('caption', '').strip()
#         tags_form = request.POST.get('tags', '').strip()
#         pictures = request.FILES.getlist('pictures')
#         remove_images = request.POST.getlist('remove_images')

#         # Check if removing caption without picture or removing picture without caption
#         has_existing_images = post.pictures.exclude(id__in=remove_images).exists()  # Remaining images after removal
#         is_caption_empty = not caption
#         is_picture_empty = not pictures and not has_existing_images

#         if is_caption_empty and not post.pictures.exists():
#             messages.error(request, "You cannot remove the caption unless a picture is provided.")
#             return render(request, 'editpost.html', {'post': post})

#         if is_picture_empty and not caption:
#             messages.error(request, "You cannot remove the picture unless a caption is provided.")
#             return render(request, 'editpost.html', {'post': post})

#         # Update the post's caption (allow blank)
#         post.caption = caption

#         # Handle tags
#         if tags_form:
#             post.tags.clear()  # Remove all existing tags
#             tag_list = tags_form.split(',')
#             for tag in tag_list:
#                 t, created = Tag.objects.get_or_create(title=tag.strip())
#                 post.tags.add(t)
#         elif not tags_form:
#             post.tags.clear()  # Remove all tags if no tags are provided

#         # Handle image removal
#         for image_id in remove_images:
#             post.pictures.filter(id=image_id).delete()

#         # Handle new pictures
#         if pictures:
#             for picture in pictures:
#                 PostImage.objects.create(post=post, image=picture)

#         post.save()  # Save changes
#         messages.success(request, "Post updated successfully!")
#         return redirect('post-details', post.id)

#     return render(request, 'editpost.html', {'post': post})

@csrf_exempt
@login_required
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':  
            try:
                post = Post.objects.get(id=post_id)
                if request.user == post.user:
                    post.delete()
                    # return HttpResponse(status=200)
                    return HttpResponseRedirect(reverse('profile', args=[request.user.username]))
                else:
                    return HttpResponse(status=403)  # Forbidden
            except Post.DoesNotExist:
                return HttpResponse(status=404)  # Not Found
        else:
            return HttpResponse("Invalid request method", status=405)  # Method Not Allowed
    else:
        return HttpResponseRedirect(reverse('sign-in'))
    
@login_required
@csrf_exempt
def edit_comment(request, comment_id):
    if request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id, user=request.user)
            data = json.loads(request.body)  # Parse the incoming JSON body
            new_body = data.get('body', '').strip()

            if not new_body:
                return JsonResponse({"success": False, "error": "Comment body cannot be empty."})

            comment.body = new_body
            comment.save()

            # Return the updated body in the response
            return JsonResponse({"success": True, "new_body": new_body})

        except Comment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Comment not found or not authorized."})

    return JsonResponse({"success": False, "error": "Invalid request method."})




@login_required
@csrf_exempt
def delete_comment(request, comment_id):
    if request.method == "POST":
        try:
            # Get the comment belonging to the user
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            
            # Delete the comment
            comment.delete()
            return JsonResponse({"success": True})

        except Comment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Comment not found or unauthorized."})
    return JsonResponse({"success": False, "error": "Invalid request method."})


