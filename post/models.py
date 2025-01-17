from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.urls import reverse
import uuid
from notification.models import Notification
from django.db import models
import uuid
from django.utils import timezone


# uploading user files to a specific directory
# def user_directory_path(instance, filename):
#     return 'user_{0}/{1}'.format(instance.user.id, filename)

def user_directory_path(instance, filename):
    # Access the user through the related post
    return f"user_{instance.post.user.id}/{filename}"


class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True, default=uuid.uuid1)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caption = models.CharField(max_length=30000, verbose_name="Caption")
    posted = models.DateField(auto_now_add=True)
    # posted = models.DateTimeField(auto_now_add=True) 
    tags = models.ManyToManyField(Tag, related_name="tags")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    likers = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    savers = models.ManyToManyField(User, blank=True, related_name='saved_posts')

    def get_absolute_url(self):
        return reverse("post-details", args=[str(self.id)])
    
    def get_likers_names(self):
        return [liker.username for liker in self.likers.all()]
    
    def __str__(self):
        return f"{self.user.username} posts {self.caption[:7]}"

class PostImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, related_name="pictures", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)
    # video = models.ImageField(upload_to=user_directory_path,null=True,blank=True)
    uploaded = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification(sender=sender, user=following, notification_types=3)
        notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification.objects.filter(sender=sender, user=following, notification_types=3)
        notify.delete()
    
    # def followers_names(self):
    #     return [follower.username for follower in self.follower.all()]
    
    # def followings_names(self):
    #     return [followings.username for followings in self.following.all()]

class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)

        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Follow.user_follow, sender=Follow)
post_delete.connect(Follow.user_unfollow, sender=Follow)