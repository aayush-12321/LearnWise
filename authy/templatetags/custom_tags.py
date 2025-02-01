from django import template
from django.urls import reverse
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

register = template.Library()

@register.simple_tag
def get_user_rating_url(profile_user, request_user):
    if profile_user == request_user:
        return reverse('user_ratings', args=[profile_user.id])
    return reverse('rate_user', args=[profile_user.id])

def reverse_geocode_with_retry(loc, latitude, longitude, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return loc.reverse((latitude, longitude), timeout=10)
        except (GeocoderTimedOut, GeocoderUnavailable):
            retries += 1
            time.sleep(1)
    return None

@register.filter
def human_readable_location(location):
    loc = Nominatim(user_agent="GetLoc")
    try:
        lat, lon = map(float, location.split(','))
        reverse_geocode_result = reverse_geocode_with_retry(loc, lat, lon)
        return reverse_geocode_result.address if reverse_geocode_result else location
    except ValueError:
        return location

