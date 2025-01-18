from directs.views import inbox, Directs, SendDirect, UserSearch, NewConversation, map_view,CallView,GenerateToken,videocall,joinVideoCall,location
from django.urls import path

from directs.consumers import CallConsumer

urlpatterns = [
    path('', inbox, name="message"),
    path('direct/<username>', Directs, name="directs"),
    path('send/', SendDirect, name="send-directs"),
    path('search/', UserSearch, name="search-users"),
    path('new/<username>', NewConversation, name="conversation"),
    path('map/', map_view, name='map_view'),
    path('location/<username>', location, name='location'),
    path('call/<username>', CallView, name="call"),
    path('generate-token/', GenerateToken, name="generate-token"),
    path('videocall/', videocall, name="videocall"),

    # path('videocall/', joinVideoCall, name="join-videocall"),

    
]

websocket_urlpatterns = [
    path('ws/call/<room_name>/', CallConsumer.as_asgi()),
]