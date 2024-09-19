from django.urls import path
from .views import get_user, create_user, user_action

urlpatterns = [
    path('users/', get_user, name='get_user'),
    path('users/create_user', create_user, name='create_user'),
    path('users/<int:pk>', user_action, name='user_action'),
]