from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse

# from post.models import Post, Tag, Follow, Stream, Likes
from post.models import Post, Tag, Follow, Stream
from django.contrib.auth.models import User
from post.forms import NewPostform
from authy.models import Profile
from django.urls import resolve
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator
from django.db.models import Count

from django.db.models import Q
# from post.models import Post, Follow, Stream

from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

# @login_required
# def index(request):
#     user = request.user
#     following_ids = set(Follow.objects.filter(follower=user).values_list('following', flat=True))
#     mutual_follow_ids = set(Follow.objects.filter(following=user).values_list('follower', flat=True)).intersection(following_ids)
    
#     own_posts = Post.objects.filter(user=user)
#     following_posts = Post.objects.filter(user__in=following_ids)
#     mutual_posts = Post.objects.filter(user__in=mutual_follow_ids)
#     other_posts = Post.objects.exclude(user__in=following_ids).exclude(user=user)

#     all_posts = own_posts | following_posts | mutual_posts | other_posts
#     scored_posts = []
#     liked_by=[]
#     saved_by=[]


#     # Calculate post scores with a priority for followed users
#     for post in all_posts:
#         if post.user.id in following_ids:
#             # Higher priority for followed users
#             relationship_multiplier = 2.0
#             like_weight = 2.5
#             comment_weight = 2.0
#             recency_decay = 1.1  # Slower decay for followed users
#         elif post.user == user:
#             relationship_multiplier = 1.25
#             like_weight = 1.8
#             comment_weight = 1.5
#             recency_decay = 1.25
#         elif post.user.id in mutual_follow_ids:
#             relationship_multiplier = 1.2
#             like_weight = 1.8
#             comment_weight = 1.4
#             recency_decay = 1.3
#         else:
#             relationship_multiplier = 1.0
#             like_weight = 1.5
#             comment_weight = 1.2
#             recency_decay = 1.5

#         # Engagement scores
#         likes = post.likes
#         comments_count = post.comment.count()
        
#         # Recency factor with customized decay based on relationship
#         days_since_post = (timezone.now().date() - post.posted).days
#         recency_factor = recency_decay ** days_since_post

#         # Calculate the final score, applying the customized weights
#         score = ((likes + 1) * like_weight + (comments_count + 1) * comment_weight) / recency_factor
#         score *= relationship_multiplier

#         #
        
#         likers = [like.user.username for like in Likes.objects.filter(post=post)]
#         savers = [profile.user.username for profile in Profile.objects.filter(favourite=post)]
#         # print(post.caption)
#         # print(f'Likers: {likers}')
#         # print(f'savers: {savers}')

#         scored_posts.append((post, score))
#         liked_by.append(likers)
#         saved_by.append(saved_by)

#     # Sort posts by score in descending order
#     scored_posts.sort(key=lambda x: x[1], reverse=True)
#     sorted_posts = [post for post, _ in scored_posts]

#      # Handle search query if present
#     query = request.GET.get('q')
#     if query:
#         users = User.objects.filter(Q(username__icontains=query))
#         paginator = Paginator(users, 6)
#         page_number = request.GET.get('page')
#         users_paginator = paginator.get_page(page_number)

#     # Suggestions based on mutual friends
#     followings = []
#     suggestions = []
#     if request.user.is_authenticated:
#         followings = set(Follow.objects.filter(follower=request.user).values_list('following', flat=True))
#         potential_suggestions = User.objects.exclude(pk__in=followings).exclude(pk=request.user.pk)
        
#         suggestions_with_mutuals = []
#         for user in potential_suggestions:
#             mutual_friends_count = Follow.objects.filter(following=user).filter(follower__in=followings).count()
#             suggestions_with_mutuals.append((user, mutual_friends_count))
        
#         sorted_suggestions = sorted(suggestions_with_mutuals, key=lambda x: x[1], reverse=True)[:6]
#         suggestions = [user for user, _ in sorted_suggestions]

#     # Prepare context and render template
#     context = {
#         'post_items': sorted_posts,
#         'profile': Profile.objects.all(),
#         'follow_status': Follow.objects.filter(following=user, follower=request.user).exists(),
#         'all_users': User.objects.all(),
#         'suggestions': suggestions,
#         # 'saved_by':saved_by,
#         # 'liked_by':liked_by,
#         # 'liked_post_ids': list(liked_post_ids),
#         # 'saved_post_ids': list(saved_post_ids),
#         # 'post_items': posts_with_status,
#         # 'users_paginator': users_paginator,
#         # 'comments_count' : post.comment.count()
#     }
#     return render(request, 'index.html', context)


from django.db.models import Q
from django.core.paginator import Paginator
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
        if post.user.id in following_ids:
            relationship_multiplier = 2.0
            like_weight = 2.5
            comment_weight = 2.0
            recency_decay = 1.1
        elif post.user == user:
            relationship_multiplier = 1.25
            like_weight = 1.8
            comment_weight = 1.5
            recency_decay = 1.25
        elif post.user.id in mutual_follow_ids:
            relationship_multiplier = 1.2
            like_weight = 1.8
            comment_weight = 1.4
            recency_decay = 1.3
        else:
            relationship_multiplier = 1.0
            like_weight = 1.5
            comment_weight = 1.2
            recency_decay = 1.5

        likes = post.likes
        comments_count = post.comment.count()
        days_since_post = (timezone.now().date() - post.posted).days
        recency_factor = recency_decay ** days_since_post

        score = ((likes + 1) * like_weight + (comments_count + 1) * comment_weight) / recency_factor
        score *= relationship_multiplier
        scored_posts.append((post, score))

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

    sorted_suggestions = sorted(suggestions_with_mutuals, key=lambda x: x[1], reverse=True)[1:7]
    suggestions = [user for user, _ in sorted_suggestions]

    # Prepare context and render template
    context = {
        'post_items': sorted_posts,
        'liked_post_ids': list(liked_post_ids),
        'saved_post_ids': list(saved_post_ids),
        'suggestions': suggestions,
    }
    return render(request, 'index.html', context)





@login_required
def NewPost(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    tags_obj = []

    if request.method == "POST":
        picture = request.FILES.get('picture')
        caption = request.POST.get('caption')
        tag_form = request.POST.get('tags')
        
        if picture and caption:
            tag_list = tag_form.split(',') if tag_form else []

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag.strip())
                tags_obj.append(t)
            
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user=user)
            p.tags.set(tags_obj)
            p.save()
            return redirect('profile', request.user.username)

    context = {
        'profile': profile
    }
    return render(request, 'newpost.html', context)


# @login_required
# def NewPost(request):
#     user = request.user
#     profile = get_object_or_404(Profile, user=user)
#     tags_obj = []
    
#     if request.method == "POST":
#         form = NewPostform(request.POST, request.FILES)
#         if form.is_valid():
#             picture = form.cleaned_data.get('picture')
#             caption = form.cleaned_data.get('caption')
#             tag_form = form.cleaned_data.get('tags')
#             tag_list = list(tag_form.split(',')) if tag_form else []

#             for tag in tag_list:
#                 t, created = Tag.objects.get_or_create(title=tag.strip())
#                 tags_obj.append(t)
#             p, created = Post.objects.get_or_create(
#                 picture=picture,
#                 caption=caption,
#                 user=user
#             )
#             p.tags.set(tags_obj)
#             p.save()
#             return redirect('profile', request.user.username)
#     else:
#         form = NewPostform()
#     context = {'form': form}
#     return render(request, 'newpost.html', context)


@login_required
def PostDetail(request, post_id):
    
    post = get_object_or_404(Post, id=post_id)

    # print(post.get_likers_names())
    # print("#"*20)

    user = request.user

    # Identify liked and saved posts
    liked_post_ids = Post.objects.filter(likers=user).values_list('id', flat=True)
    saved_post_ids = Post.objects.filter(savers=user).values_list('id', flat=True)


    #comments
    comments = Comment.objects.filter(post=post).order_by('-date')

    if request.method == "POST":
        # form = NewCommentForm(request.POST)
        form = NewCommentForm(request.POST,request.FILES)
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
        'comments': comments,
        'liked_post_ids': list(liked_post_ids),
        'saved_post_ids': list(saved_post_ids),

    }
    # for comment in comments:
        # print(f"Name:{comment.user.profile.first_name}")
        # print("*"*20)
        # print(f"Name:{comment.user.first_name}")

    return render(request, 'postdetail.html', context)

@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'tag.html', context)


# # Like function
# @login_required
# def like(request, post_id):
#     user = request.user
#     post = Post.objects.get(id=post_id)
#     current_likes = post.likes
#     liked = Likes.objects.filter(user=user, post=post).count()

#     if not liked:
#         Likes.objects.create(user=user, post=post)
#         current_likes = current_likes + 1
#     else:
#         Likes.objects.filter(user=user, post=post).delete()
#         current_likes = current_likes - 1
        
#     post.likes = current_likes
#     post.save()
#     # return HttpResponseRedirect(reverse('post-details', args=[post_id]))
#     return HttpResponseRedirect(reverse('post-details', args=[post_id]))




# @login_required
# def favourite(request, post_id):
#     user = request.user
#     post = Post.objects.get(id=post_id)
#     profile = Profile.objects.get(user=user)

#     if profile.favourite.filter(id=post_id).exists():
#         profile.favourite.remove(post)
#     else:
#         profile.favourite.add(post)
#     return HttpResponseRedirect(reverse('post-details', args=[post_id]))


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
    context = {
        'post': post,
        'likers': likers,
    }
    return render(request, 'likers.html', context)


@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delete = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('sign-in'))
    


@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()
            
            if(post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if(post.content_image):
                post_image = post.img_url()
            else:
                post_image = False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            return JsonResponse({
                "success": False
            })
    else:
            return HttpResponse("Method must be 'POST'")


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def toggle_like(request, post_id):
#     post = Post.objects.get(id=post_id)
#     like, created = Likes.objects.get_or_create(user=request.user, post=post)
#     if not created:
#         like.delete()  # Unlike the post if it was already liked
#     return JsonResponse({'status': 'success'})

# @csrf_exempt
# def toggle_save(request, post_id):
#     profile = request.user.profile
#     post = Post.objects.get(id=post_id)
#     if post in profile.favourite.all():
#         profile.favourite.remove(post)  # Unsaving the post
#     else:
#         profile.favourite.add(post)  # Saving the post
#     return JsonResponse({'status': 'success'})
