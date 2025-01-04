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
    bio = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    # favourite = models.ManyToManyField(Post, blank=True)
    favourite = models.ManyToManyField(Post, blank=True)

    ############
    # The reason "Learner" and "Mentor" are written twice in ROLE_CHOICES is because the first value 
    # in each tuple represents the value that will be stored in the database, and the second value is the
    # human-readable name that will be displayed in the interface (such as a form or a dropdown). In this case,
    # both the stored value and the displayed name for each role are the same.

    # New fields
    ROLE_CHOICES = [
        ('Mentor', 'Mentor'),
        ('Learner', 'Learner'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False, blank=False, default='Learner')
    skills = models.TextField(help_text="List of skills you can share (separated by commas)", null=True, blank=True)
    interests = models.TextField(help_text="Skills or areas you'd like to learn (separated by commas)", null=True, blank=True)
    
    
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

############
class Rating(models.Model):
    mentor = models.ForeignKey(User, related_name="mentor_ratings", on_delete=models.CASCADE)
    learner = models.ForeignKey(User, related_name="learner_ratings", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Rating out of 5
    feedback = models.TextField()  # Optional feedback from the learner
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating from {self.learner.username} to {self.mentor.username} - {self.rating}/5"

##############

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
