import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_user_signup(api_client):
    url = reverse('signup')
    signup_data = { "username": "test", "password": "test1234", "email": "test@mail.com" }

    response = api_client.post(url, signup_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.filter(email='test@mail.com').exists()
    assert user is True


@pytest.mark.django_db
def test_user_login(api_client, django_user_model):
    user = User.objects.create_user(email='testuser@example.com',username='test', password='password')
    url = reverse('login')
    login_data = {
        'email': 'testuser@example.com',
        'username': 'test',
        'password': 'password'
    }
    response = api_client.post(url, login_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data