from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from notification.models import Notification
from post.models import Post
from comment.models import Comment
from django.contrib.auth.models import User
from post.models import Post, Follow

# Signal when a user follows another user
@receiver(post_save, sender=Follow)
def user_follow(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.follower,
            user=instance.following,
            notification_types=3  # Follow notification
        )


# Signal when a user unfollows another user
@receiver(post_delete, sender=Follow)
def user_unfollow(sender, instance, **kwargs):
    Notification.objects.filter(
        sender=instance.follower,
        user=instance.following,
        notification_types=3
    ).delete()


# Signal when a user likes a post
@receiver(m2m_changed, sender=Post.likers.through)
def create_like_notification(sender, instance, action, pk_set, **kwargs):
    """
    This signal is triggered when a new user likes a post. It creates a notification
    for the post owner that someone liked their post.
    """
    if action == "post_add":  # Trigger when a new like is added
        for liker_id in pk_set:
            liker = User.objects.get(pk=liker_id)
            Notification.objects.create(
                sender=liker,
                user=instance.user,  # Notify the post owner
                post=instance,
                notification_types=1  # Like notification type
            )


# Signal when a user comments on a post
@receiver(post_save, sender=Comment)
def user_comment_post(sender, instance, created, **kwargs):
    if created:  # Only create a notification if a new comment is created
        post = instance.post
        sender = instance.user
        text_preview = instance.body[:90]  # Show the first 90 characters of the comment

        # Avoid notifying the user if they comment on their own post
        if sender != post.user:
            Notification.objects.create(
                post=post,
                sender=sender,
                user=post.user,
                text_preview=text_preview,
                notification_types=2  # Comment notification type
            )


# Signal when a comment is deleted (e.g., user removes a comment)
@receiver(post_delete, sender=Comment)
def user_del_comment_post(sender, instance, **kwargs):
    post = instance.post
    sender = instance.user
    Notification.objects.filter(
        post=post,
        sender=sender,
        user=post.user,
        notification_types=2  # Only remove comment notifications
    ).delete()


# Signal when a user creates a new post
@receiver(post_save, sender=Post)
def create_new_post_notification(sender, instance, created, **kwargs):
    if created:  # Only notify when a new post is created
        followers = instance.user.following.all()  # Get followers of the user
        for follower in followers:
            Notification.objects.create(
                sender=instance.user,
                user=follower,
                post=instance,
                notification_types=4  # New post notification type
            )
