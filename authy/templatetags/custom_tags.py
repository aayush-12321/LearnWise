from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def get_user_rating_url(profile_user, request_user):
    if profile_user == request_user:
        return reverse('user_ratings', args=[profile_user.id])
    return reverse('rate_user', args=[profile_user.id])
