from django.urls import path
from .views import (
    signup, login, send_friend_request,
accept_friend_request, reject_friend_request, list_friends, list_pending_requests, search_users,
ListUsersView, block_user, unblock_user
)
from .utils import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('refresh_token/', CustomTokenRefreshView.as_view(), name='get_fresh_token'),
    path('token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('send_friend_request/', send_friend_request, name='send_friend_request'),
    path('accept_friend_request/', accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/', reject_friend_request, name='reject_friend_request'),
    path('list_friends/', list_friends, name='list_friends'),
    path('list_pending_requests/', list_pending_requests, name='list_pending_requests'),
    path('block_user/', block_user, name='block_user'),
    path('unblock_user/', unblock_user, name='unblock_user'),
    path('search_users/', search_users, name='search_users'),
    path('get_all_users/', ListUsersView.as_view(), name='get_all_users'),
]