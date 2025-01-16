
from django.shortcuts import redirect, render, get_object_or_404,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from directs.models import Message
from post.models import Follow
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
from django.utils.html import escape
import time
from django.core.exceptions import ObjectDoesNotExist


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
        # 'messages': message_paginator,
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
    
    directs = directs.order_by('date')  # Order alphabetically by first name

    paginator = Paginator(directs, 4)
    page_number = request.GET.get('page')
    message_paginator = paginator.get_page(page_number)

        # Determine the last page number
    last_page_number = paginator.num_pages

    # Redirect to the last page if no page number is provided or invalid
    if not page_number or not page_number.isdigit() or int(page_number) > last_page_number:
        return HttpResponseRedirect(f'?page={last_page_number}')


    context = {
        # 'directs': directs,
        'directs': message_paginator,
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


# def UserSearch(request):
#     query = request.GET.get('q')
#     context = {}
#     if query:
#         users = User.objects.filter(Q(username__icontains=query))

#         # Paginator
#         paginator = Paginator(users, 8)
#         page_number = request.GET.get('page')
#         users_paginator = paginator.get_page(page_number)

#         context = {
#             'users': users_paginator,
#             }

#     return render(request, 'directs/search.html', context)

def UserSearch(request):
    query = request.GET.get('q', '').strip()  # Search query
    selected_skills = request.GET.getlist('skills')  # Selected skills for filtering
    searched_skill = request.GET.get('searched_skill', None)  # Filter by searched skill
    role_filter = request.GET.get('role', '')  # Role filter (Mentor/Learner)

    # Base queryset: all users
    users = User.objects.all()
    filtered_users = User.objects.none()  # Start with an empty queryset
    search_by_name_success = False

    # Apply query filtering if provided
    if query:
        # If searched_skill is checked and query length > 2, include skill-based search
        if searched_skill and len(query) > 1:
            skill_users = users.filter(profile__skills__icontains=query)
            filtered_users = filtered_users | skill_users
        else:
            filtered_users = users.filter(
                Q(username__icontains=query) |
                Q(profile__first_name__icontains=query) |
                Q(profile__last_name__icontains=query)
            )
            search_by_name_success = filtered_users.exists()
    
    # If no results from name search and skill search is enabled
    if not search_by_name_success and len(query) > 1:
        skill_users = users.filter(profile__skills__icontains=query)
        filtered_users = filtered_users | skill_users
        searched_skill = "searched_skill"  # Ensure the checkbox remains checked

    # Apply skill filters if selected
    if selected_skills:
        skill_filters = Q()
        for skill in selected_skills:
            skill_filters |= Q(profile__skills__icontains=skill)
        filtered_users = filtered_users.filter(skill_filters) if query else users.filter(skill_filters)

    # Apply role filtering
    if role_filter in ['Mentor', 'Learner']:
        filtered_users = filtered_users.filter(profile__role=role_filter)

    # Retrieve the 10 most used skills
    all_skills = Profile.objects.values_list('skills', flat=True)
    skill_counts = {}
    for skill_list in all_skills:
        if skill_list:
            for skill in skill_list.split(','):
                skill = skill.strip().lower()
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    most_used_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Paginator
    paginator = Paginator(filtered_users, 6)
    page_number = request.GET.get('page')
    users_paginator = paginator.get_page(page_number)

    context = {
        'users': users_paginator,
        'most_used_skills': [skill[0] for skill in most_used_skills],
        'selected_skills': selected_skills,
        'role_filter': role_filter,
        'searched_skill': searched_skill,  # Maintain checkbox state
        'query': query,  # To retain the query in the template
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


# def geocode_with_retry(loc, address, max_retries=3):
#     retries = 0
#     while retries < max_retries:
#         try:
#             return loc.geocode(address, timeout=10)
#         except (GeocoderTimedOut, GeocoderUnavailable):
#             retries += 1
#             time.sleep(1)
#     return None

# def map_view(request):
#     # Assuming logged-in user's profile can be accessed through request.user.profile
#     user_profile = Profile.objects.filter(user=request.user).first()
    
#     if not user_profile:
#         return render(request, 'directs/not_found.html')

#     loc = Nominatim(user_agent="GetLoc")
#     user_location = f"{user_profile.location}, Nepal"
#     geocode_result = geocode_with_retry(loc, user_location)

#     if geocode_result:
#         user_latitude, user_longitude = geocode_result.latitude, geocode_result.longitude
#     else:
#         user_latitude, user_longitude = 27.6800062, 85.3857303  # Default location if geocoding fails

#     # Initialize a Folium map
#     m = folium.Map(location=[user_latitude, user_longitude], zoom_start=10, control_scale=True)

#     # Retrieve all profiles and add markers, excluding the logged-in user’s profile
#     profiles = Profile.objects.exclude(user=request.user)
#     for profile in profiles:
#         location_str = f"{profile.location}, Nepal"
#         loc_result = geocode_with_retry(loc, location_str)

#         if loc_result:
#             lat, lon = loc_result.latitude, loc_result.longitude
#             distance = geodesic((user_latitude, user_longitude), (lat, lon)).km

#             # Profile details for popup
#             # profile_image_url = profile.image.url if profile.image.url else '/path/to/default/image.jpg'
#             profile_name = escape(profile.user.username)
#             profile_bio = escape(profile.bio or "No bio available")

#             popup_content = f"""
#                 <div style="text-align: center;">
                   
#                     <p><strong>{profile_name}</strong></p>
#                     <p><em>{profile_bio}</em></p>
#                     <p>Location: {escape(profile.location)}</p>
#                     <p>Distance: {distance:.2f} km</p>
#                 </div>
#             """
#             iframe = branca.element.IFrame(html=popup_content, width=250, height=150)
#             folium.Marker([lat, lon], popup=folium.Popup(iframe)).add_to(m)

#     # Render the map in HTML
#     m = m._repr_html_()  # Convert map to HTML

#     return render(request, 'directs/map_view.html', {'map': m})


def geocode_with_retry(loc, address, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return loc.geocode(address, timeout=10)
        except (GeocoderTimedOut, GeocoderUnavailable):
            retries += 1
            time.sleep(1)
    return None

def reverse_geocode_with_retry(loc, latitude, longitude, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return loc.reverse((latitude, longitude), timeout=10)
        except (GeocoderTimedOut, GeocoderUnavailable):
            retries += 1
            time.sleep(1)
    return None

@login_required
def map_view(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect('sign-in')  # Redirect to the login page if the profile is not found
    
    loc = Nominatim(user_agent="GetLoc")
    user_location = f"{user_profile.location}, Nepal"
    geocode_result = geocode_with_retry(loc, user_location)

    if geocode_result:
        user_latitude, user_longitude = geocode_result.latitude, geocode_result.longitude
    else:
        user_latitude, user_longitude = 27.6800062, 85.3857303  # Default location if geocoding fails

    # Get the users that the logged-in user is following
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)

    # Filter profiles with valid locations and in the following list
    valid_profiles = Profile.objects.filter(user__in=following_users, location__isnull=False).exclude(location__exact="")
    # print(valid_profiles)
    valid_profiles = valid_profiles.order_by('first_name')  # Order alphabetically by first name
    # print(valid_profiles)

    # Paginate the valid profiles
    valid_profiles = valid_profiles.order_by('first_name')  # Order alphabetically by first name
    # print(valid_profiles)
    paginator = Paginator(valid_profiles, 5)  # Show 5 profiles per page
    page_number = request.GET.get('page')
    profiles_page = paginator.get_page(page_number) 

    # Initialize a Folium map
    m = folium.Map(location=[user_latitude, user_longitude], zoom_start=10, control_scale=True)

    profile_urls = {}
    location_groups = {}

    for profile in profiles_page:  # Only include profiles on the current page
        try:
            lat, lon = map(float, profile.location.split(','))
            reverse_geocode_result = reverse_geocode_with_retry(loc, lat, lon)
            human_readable_location = reverse_geocode_result.address if reverse_geocode_result else profile.location
        except ValueError:
            location_str = f"{profile.location}"
            loc_result = geocode_with_retry(loc, location_str)
            if loc_result:
                lat, lon = loc_result.latitude, loc_result.longitude
                human_readable_location = location_str
            else:
                continue  # Skip profiles with invalid location

        distance = geodesic((user_latitude, user_longitude), (lat, lon)).km

        if (lat, lon) not in location_groups:
            location_groups[(lat, lon)] = []

        # Append the profile to the appropriate location group
        location_groups[(lat, lon)].append((profile, human_readable_location))

    # Iterate over location groups and add markers to the map
    for (lat, lon), profiles in location_groups.items():
        popup_content = "<div style='text-align: center;'>"
        for profile, human_readable_location in profiles:
            first_name = profile.first_name.capitalize() if profile.first_name else ""
            last_name = profile.last_name.capitalize() if profile.last_name else ""
            full_name = f"{first_name} {last_name}".strip() or escape(profile.user.username)
            profile_bio = escape(profile.bio or "No bio available")
            profile_url = reverse('profile', args=[profile.user.username])
            profile_urls[profile.user.id] = profile_url

            popup_content += f"""
                <strong id="profile-link-{profile.user.id}" 
                        style="cursor: pointer; text-decoration: underline; color: rgb(51, 51, 51);">
                    {escape(full_name)}
                </strong>
                <p>Location: {escape(human_readable_location)}</p>
                <p>Distance: {distance:.2f} km</p>
                <hr>
            """
        popup_content += "</div>"

        # Add the marker and popup
        iframe = branca.element.IFrame(html=popup_content, width=250, height=150)
        popup = folium.Popup(iframe)
        marker = folium.Marker([lat, lon], popup=popup)
        m.add_child(marker)

    m = m._repr_html_()  # Convert map to HTML

    return render(request, 'directs/map_view.html', {'map': m, 'profiles_page': profiles_page, 'profile_urls': profile_urls})


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