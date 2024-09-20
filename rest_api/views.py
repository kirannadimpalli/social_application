from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetails
from rest_api.models import CustomUser
from django.shortcuts import get_object_or_404
from .serializer import UserSerializers, CredSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


@api_view(['GET'])
def get_user(request):
    user = UserDetails.objects.all()
    serializer = UserSerializers(user, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializers(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','DELETE', 'PUT'])
def user_action(request, pk):
    try:
        user = UserDetails.objects.get(pk=pk)
    except user.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        serializer = UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserSerializers(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = CredSerializer(data=request.data)
    if serializer.is_valid():
        user = get_user_model().objects.create_user(
            email=request.data['email'], 
            password=request.data['password']
        )
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def login(request):
    user = get_object_or_404(CustomUser, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = CredSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed!")
