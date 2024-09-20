import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_api.models import CustomUser
from rest_api.models import UserDetails

@pytest.fixture
def api_client():
    return APIClient()

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
def test_fetch_user(api_client):
    url = reverse('get_user')
    UserDetails.objects.create(name='kiran', age=25)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == 'kiran'

@pytest.mark.django_db
def test_create_user(api_client):
    url = reverse('create_user')
    user_data = {
        'name': 'john',
        'age': 34
    }
    response = api_client.post(url, user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == 'john'
    assert response.json()['age'] == 34


@pytest.mark.django_db
def test_authorization(api_client):
    url = reverse('signup')
    signup_data = {"password": "test1234", "email": "test@mail.com" }
    response = api_client.post(url, signup_data, format='json')

    url = reverse('get_token')
    login_data = {"password": "test1234", "email": "test@mail.com" }
    response = api_client.post(url, login_data, format='json')
    access_token = response.json().get('access')
    assert access_token is not None, "Access token was not retrieved."

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('test_token')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_fail_authorization(api_client):
    access_token = 'dakjbasjbdlasjd'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('test_token')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
