from django.db import models
from django.contrib.auth.models import User
import PIL 
from PIL import Image
from django.db.models.base import Model
from django.db.models.fields import DateField
from django.urls import reverse
from django.db.models.signals import post_save
import uuid
from django.utils import timezone
from post.models import Post


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_pciture", null=True, default="default.png")
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    # bio = models.CharField(max_length=800, null=True, blank=True)
    bio = models.TextField(max_length=800, null=True, blank=True)
    # location = models.CharField(max_length=200, null=True, blank=True)
    location = models.TextField(max_length=300, null=True, blank=True)

    url = models.URLField(max_length=200, null=True, blank=True)
    # favourite = models.ManyToManyField(Post, blank=True)
    favourite = models.ManyToManyField(Post, blank=True)

    ROLE_CHOICES = [
        ('Mentor', 'Mentor'),
        ('Learner', 'Learner'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False, blank=False, default='Learner')
    skills = models.TextField(help_text="List of skills you can share (separated by commas)", null=True, blank=True,max_length=500)
    interests = models.TextField(help_text="Skills or areas you'd like to learn (separated by commas)", null=True, blank=True,max_length=500)
    
    
    # Add relationships for rating/feedback (for Mentors)
    ratings = models.ManyToManyField('Rating', blank=True, related_name='rated_profile')

    # #########

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Rating(models.Model):
    RATING_CHOICES = [
        ('mentorship', 'Mentorship'),
        ('learning', 'Learning'),
    ]

    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rate_type = models.CharField(max_length=20, choices=RATING_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reviewer', 'rated_user', 'rate_type'], name='unique_rating')
        ]

    def __str__(self):
        return f"Rating by {self.reviewer.username} for {self.rated_user.username} ({self.rate_type})"


##############

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
