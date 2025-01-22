from django.urls import path
from post.views import index, NewPost, PostDetail, Tags,like,favourite,delete_post,edit_post,post_likers,edit_comment,delete_comment

urlpatterns = [
    path('', index, name='index'),
    path('newpost/', NewPost, name='newpost'),
    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    # path('<uuid:post_id>/like',like,name='like'),
    path('like/<uuid:post_id>/', like, name='like'),
    
    path('post/<uuid:post_id>/likers/', post_likers, name='post-likers'),
    path('<uuid:post_id>/favourite', favourite, name='favourite'),
    # path('follow/<int:user_id>/<str:follow_type>/', followers_followings_list, name='follow_list'),

    
    # path("n/post/<int:post_id>/delete", delete_post, name="deletepost"),
    # path("n/post/<int:post_id>/edit", edit_post, name="editpost"),
    
    path('post/<uuid:post_id>/edit/', edit_post, name='edit_post'),
    # path('<uuid:post_id>/delete/', delete_post, name='delete-post'),
    path('<uuid:post_id>/delete/', delete_post, name='delete-post'),


    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    #  path('<int:comment_id>/delete/', delete_comment, name='delete_comment'),






]
