import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_api.models import CustomUser
from django.test import override_settings
import uuid
from django.core.cache import cache

@pytest.fixture
def api_client():
    return APIClient()


# @pytest.mark.django_db
# @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': []})
# def test_authorization(api_client):
#     url = reverse('signup')
#     signup_data = {"password": "test1234", "email": "test@mail.com"}
#     response = api_client.post(url, signup_data, format='json')
#     assert response.status_code == status.HTTP_201_CREATED, "Signup failed."
#     url = reverse('get_token')
#     login_data = {"password": "test1234", "email": "test@mail.com"}
    
#     response = api_client.post(url, login_data, format='json')
#     assert response.status_code == status.HTTP_200_OK, "Token request failed."
#     access_token = response.json().get('access')
    
#     assert access_token is not None, "Access token was not retrieved."

#     api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
#     url = reverse('test_token') 
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK, "Authorized request failed."

@pytest.mark.django_db
def test_user_signup(api_client):
    url = reverse('signup')
    signup_data = { "password": "test1234", "email": "test@mail.com" }

    response = api_client.post(url, signup_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    user = CustomUser.objects.filter(email='test@mail.com').exists()
    assert user is True


@pytest.mark.django_db
def test_user_login(api_client, django_user_model):
    user = CustomUser.objects.create_user(email='testuser@example.com', password='password')
    url = reverse('login')
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password'
    }
    response = api_client.post(url, login_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data


@pytest.mark.django_db
def test_fail_authorization(api_client):
    access_token = 'dakjbasjbdlasjd'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('test_token')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.skip
def test_login_rate_limiting(api_client):
    cache.clear()
    user = CustomUser.objects.create_user(email='testuser@example.com', password='password')

    url = reverse('login')

    login_data = {"email": 'testuser@example.com', "password": 'password'}

    for i in range(5):
        response = api_client.post(url, login_data, format='json')
        assert response.status_code == status.HTTP_200_OK, f"Login attempt {i+1} should succeed."

    response = api_client.post(url, login_data, format='json')

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, "Rate limiting should trigger after 5 requests."
    assert response.data == {"detail": "Request was throttled. Expected available in 60 seconds."}