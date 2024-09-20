from django.urls import path
from .views import (
    get_user, create_user, user_action, signup, login, test_token, send_friend_request,
accept_friend_request, reject_friend_request, list_friends, list_pending_requests, search_users,
ListUsersView
)
from .utils import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('users/', get_user, name='get_user'),
    path('users/create_user', create_user, name='create_user'),
    path('users/<int:pk>', user_action, name='user_action'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('test_token/', test_token, name='test_token'),
    path('refresh_token/', CustomTokenRefreshView.as_view(), name='get_fresh_token'),
    path('token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('send_friend_request/', send_friend_request, name='send_friend_request'),
    path('accept_friend_request/', accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/', reject_friend_request, name='reject_friend_request'),
    path('list_friends/', list_friends, name='list_friends'),
    path('list_pending_requests/', list_pending_requests, name='list_pending_requests'),
    path('search_users/', search_users, name='search_users'),
    path('get_all_users/', ListUsersView.as_view(), name='get_all_users'),
]