from django.urls import path
from post.views import index, NewPost, PostDetail, Tags,like,favourite,delete_post,edit_post

urlpatterns = [
    path('', index, name='index'),
    path('newpost/', NewPost, name='newpost'),
    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('<uuid:post_id>/like',like,name='like'),

    path('<uuid:post_id>/favourite', favourite, name='favourite'),

    
    path("n/post/<int:post_id>/delete", delete_post, name="deletepost"),
    path("n/post/<int:post_id>/edit", edit_post, name="editpost"),
    # path('<uuid:post_id>/toggle_like/', toggle_like, name='toggle-like'),
    # path('<uuid:post_id>/toggle_save/', toggle_save, name='toggle-save'),






]
