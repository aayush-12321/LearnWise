from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, 'Like'),
        (2, 'Comment'),
        (3, 'Follow'),
        (4, 'New Post'),
    )

    post = models.ForeignKey("post.Post", on_delete=models.CASCADE, related_name="notification_post", null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user")
    notification_types = models.IntegerField(choices=NOTIFICATION_TYPES,default=1)
    text_preview = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.user}: {self.get_notification_types_display()}"


