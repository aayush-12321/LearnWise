
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from directs.models import Message
from django.contrib.auth.models import User
from authy.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator

from django.shortcuts import render
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.distance import geodesic
import folium
import branca
# from .models import User  # Assuming user data is stored in a model called User
import time
from django.utils.html import escape
from django.http import JsonResponse

@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    profile = get_object_or_404(Profile, user=user)

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
    context = {
        'directs':directs,
        'messages': messages,
        'active_direct': active_direct,
        'profile': profile,
    }
    return render(request, 'directs/direct.html', context)


@login_required
def Directs(request, username):
    user  = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)  
    directs.update(is_read=True)

    for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }
    return render(request, 'directs/direct.html', context)

def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    strip_body = request.POST.get('body', '').strip()  # Use .strip() to remove leading and trailing spaces

    if strip_body:

        followings = from_user.following.all().select_related('following')
        follow_users = [follow.following for follow in followings]
        title = f"Followings of {from_user.username}"

        if request.method == "POST":
            try:
                to_user = User.objects.get(username=to_user_username)
                # print(to_user)
                Message.sender_message(from_user, to_user, body)
                return redirect('message')
            except:
                context = {
                        'user': from_user,  # User being viewed
                        'follow_users': follow_users,  # List of followers or followings
                        'title': title,  # Title for the page
                        }
                return render(request, 'follow_list.html', context)
    else:
        return redirect('message')


def UserSearch(request):
    query = request.GET.get('q')
    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Paginator
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
            }

    return render(request, 'directs/search.html', context)

def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Message.sender_message(from_user, to_user, body)
    return redirect('message')


def geocode_with_retry(loc, address, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return loc.geocode(address, timeout=10)
        except (GeocoderTimedOut, GeocoderUnavailable):
            retries += 1
            time.sleep(1)
    return None

def map_view(request):
    # Assuming logged-in user's profile can be accessed through request.user.profile
    user_profile = Profile.objects.filter(user=request.user).first()
    
    if not user_profile:
        return render(request, 'directs/not_found.html')

    loc = Nominatim(user_agent="GetLoc")
    user_location = f"{user_profile.location}, Nepal"
    geocode_result = geocode_with_retry(loc, user_location)

    if geocode_result:
        user_latitude, user_longitude = geocode_result.latitude, geocode_result.longitude
    else:
        user_latitude, user_longitude = 27.6800062, 85.3857303  # Default location if geocoding fails

    # Initialize a Folium map
    m = folium.Map(location=[user_latitude, user_longitude], zoom_start=10, control_scale=True)

    # Retrieve all profiles and add markers, excluding the logged-in user’s profile
    profiles = Profile.objects.exclude(user=request.user)
    for profile in profiles:
        location_str = f"{profile.location}, Nepal"
        loc_result = geocode_with_retry(loc, location_str)

        if loc_result:
            lat, lon = loc_result.latitude, loc_result.longitude
            distance = geodesic((user_latitude, user_longitude), (lat, lon)).km

            # Profile details for popup
            # profile_image_url = profile.image.url if profile.image.url else '/path/to/default/image.jpg'
            profile_name = escape(profile.user.username)
            profile_bio = escape(profile.bio or "No bio available")

            popup_content = f"""
                <div style="text-align: center;">
                   
                    <p><strong>{profile_name}</strong></p>
                    <p><em>{profile_bio}</em></p>
                    <p>Location: {escape(profile.location)}</p>
                    <p>Distance: {distance:.2f} km</p>
                </div>
            """
            iframe = branca.element.IFrame(html=popup_content, width=250, height=150)
            folium.Marker([lat, lon], popup=folium.Popup(iframe)).add_to(m)

    # Render the map in HTML
    m = m._repr_html_()  # Convert map to HTML

    return render(request, 'directs/map_view.html', {'map': m})


@login_required
def CallView(request, username):
    user = request.user
    try:
        to_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('search-users')

    context = {
        'from_user': user,
        'to_user': to_user,
    }
    return render(request, 'directs/call.html', context)


@login_required
def GenerateToken(request):
    import random
    import string

    if request.method == "POST":
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        return JsonResponse({'token': token})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def videocall(request):
    profile = Profile.objects.get(user=request.user)
    # print(profile.user.username)
    return render(request,'directs/videocall.html',{'name':profile.first_name+' '+ profile.last_name })

# <!-- <a href="{% url 'call' message.user.username %}"> -->

@login_required
def joinVideoCall(request):
    profile = Profile.objects.get(user=request.user)
    # print(profile.user.username)
    return render(request,'directs/videocall.html',{'name':profile.first_name+' '+ profile.last_name })