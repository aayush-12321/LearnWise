from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from authy.views import UserProfile, editProfile,followers_followings_list

urlpatterns = [
    # Profile Section
    # path('<str:username>/', UserProfile, name='profile'),

    path('profile/edit', editProfile, name="editprofile"),
    # path('follow/<int:user_id>/<str:follow_type>/', followers_followings_list, name='follow_list'),
    path('user/<int:user_id>/<str:follow_type>/', views.followers_followings_list, name='follow_list'),


    # User Authentication
    path('sign-up/', views.register, name="sign-up"),
    path('sign-in/', auth_views.LoginView.as_view(template_name="sign-in.html", redirect_authenticated_user=True), name='sign-in'),
    # path('sign-out/', auth_views.LogoutView.as_view(template_name="sign-out.html"), name='sign-out'), 
    path("n/logout", views.logout_view, name="logout"),


    # path('ratings/<int:user_id>/', views.user_ratings, name='user_ratings'),
    # path('rate/<int:user_id>/', views.rate_user, name='rate_user'),

    path('rate/<int:user_id>/', views.rate_user, name='rate_user'),
    path('ratings/<int:rated_user_id>/', views.user_ratings, name='user_ratings'),
    path('delete-rating/<int:rating_id>/', views.delete_rating, name='delete_rating'),

]
