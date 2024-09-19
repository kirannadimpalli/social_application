from django.urls import path
from .views import get_user, create_user, user_action, signup, login, test_token

urlpatterns = [
    path('users/', get_user, name='get_user'),
    path('users/create_user', create_user, name='create_user'),
    path('users/<int:pk>', user_action, name='user_action'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('test_token/', test_token, name='test_token'),
]