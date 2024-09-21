from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import FriendRequest, Friend, BlockedUser
from rest_api.models import CustomUser
from django.shortcuts import get_object_or_404
from .serializer import CredSerializer, FriendRequestSerializer, FriendSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Q
from django.db import IntegrityError

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = CredSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = get_user_model().objects.create_user(
                email=request.data['email'].lower(), 
                password=request.data['password']
            )
        except IntegrityError as e:
            return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def login(request):
    user = get_object_or_404(CustomUser, email=request.data['email'].lower())
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = CredSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def send_friend_request(request):
    receiver_email = request.data.get('receiver_email')
    if not receiver_email:
        return Response({'error': 'receiver_email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if request.user.sent_requests.filter(created_at__gte=timezone.now() - timedelta(minutes=1)).count() >= 3:
        return Response({'error': 'You can send a maximum of 3 friend requests per minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    try:
        User = get_user_model()
        receiver = User.objects.get(email=receiver_email)
        sender = request.user

        if request.user == receiver:
            return Response({'error': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if BlockedUser.objects.filter(blocker=sender, blocked=receiver).exists():
            return Response({'error': 'You have blocked this user and cannot send a friend request.'}, status=status.HTTP_403_FORBIDDEN)

        existing_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()
        if existing_request:
            if existing_request.status == 'accepted':
                return Response({'message': 'You are already friends.'}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_request.status == 'pending':
                return Response({'message': 'Friend request already sent and pending.'}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_request.status == 'rejected':
                time_since_rejection = timezone.now() - existing_request.rejected_at
                if time_since_rejection < timedelta(hours=24):
                    return Response({'error': 'You cannot send a friend request to this user for the next 24 hours.'}, status=status.HTTP_403_FORBIDDEN)
                
        friend_request = FriendRequest(sender=sender, receiver=receiver, status='pending')
        friend_request.save()

        return Response({'message': 'Friend request sent successfully.'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'Receiver not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_friend_request(request):
    sender_email = request.data.get('sender_email', None)
    sender_name = request.data.get('sender_name', None)


    if not sender_email and not sender_name:
        return Response({'error': 'Please provide either sender email or sender name.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        User = get_user_model()
        if sender_email:
            sender = User.objects.get(email=sender_email)
        elif sender_name:
            sender = User.objects.get(name=sender_name)

        friend_request = FriendRequest.objects.get(sender=sender, receiver=request.user, status='pending')
    except User.DoesNotExist:
        return Response({'error': 'Sender not found.'}, status=status.HTTP_404_NOT_FOUND)
    except FriendRequest.DoesNotExist:
        return Response({'error': 'Friend request not found or already accepted/rejected.'}, status=status.HTTP_404_NOT_FOUND)

    friend_request.status = 'accepted'
    friend_request.save()
    Friend.objects.create(user=friend_request.sender, friend=request.user)

    return Response({'message': 'Friend request accepted.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([JWTAuthentication])
def reject_friend_request(request):
    sender_email = request.data.get('sender_email', None)

    if not sender_email:
        return Response({'error': 'Please provide the sender email.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        User = get_user_model()
        sender = User.objects.get(email=sender_email)
        receiver = request.user

        friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver, status='pending').first()

        if not friend_request:
            return Response({'error': 'No pending friend request found.'}, status=status.HTTP_404_NOT_FOUND)

        friend_request.status = 'rejected'
        friend_request.rejected_at = timezone.now()
        friend_request.save()

        return Response({'message': 'Friend request rejected successfully.'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'Sender not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([JWTAuthentication])
def block_user(request):
    blocked_email = request.data.get('blocked_email')

    if not blocked_email:
        return Response({'error': 'Please provide the email of the user to block.'}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    
    try:
        blocked_user = User.objects.get(email=blocked_email)
        BlockedUser.objects.get_or_create(blocker=request.user, blocked=blocked_user)
        return Response({'message': 'User blocked successfully.'}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unblock_user(request):
    blocked_email = request.data.get('blocked_email')

    if not blocked_email:
        return Response({'error': 'Please provide the email of the user to unblock.'}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    
    try:
        blocked_user = User.objects.get(email=blocked_email)
        BlockedUser.objects.filter(blocker=request.user, blocked=blocked_user).delete()
        return Response({'message': 'User unblocked successfully.'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    cache_key = f'friends_list_{request.user.id}'
    friends_list = cache.get(cache_key)

    if friends_list is None:
        friends = Friend.objects.filter(user=request.user).select_related('friend')
        serializer = FriendSerializer([friend.friend for friend in friends], many=True)
        
        friends_list = serializer.data
        cache.set(cache_key, friends_list, timeout=60 * 5)

    return Response({'friends': friends_list}, status=status.HTTP_200_OK)


class FriendRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_requests(request):
    pending_requests = FriendRequest.objects.filter(receiver=request.user, status='pending').order_by('-created_at')

    paginator = FriendRequestPagination()
    paginated_requests = paginator.paginate_queryset(pending_requests, request)

    serializer = FriendRequestSerializer(paginated_requests, many=True)

    return paginator.get_paginated_response(serializer.data)

class ListUsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CredSerializer


class UserPagination(PageNumberPagination):
    page_size = 10

@api_view(['GET'])
def search_users(request):
    keyword = request.query_params.get('q', '')
    if not keyword:
        return Response({'error': 'No search keyword provided.'}, status=status.HTTP_400_BAD_REQUEST)

    exact_email_match = CustomUser.objects.filter(email__iexact=keyword)
    
    if exact_email_match.exists():
        users = exact_email_match
    else:
        users = CustomUser.objects.filter(
            Q(name__icontains=keyword)
        ).distinct()

    paginator = UserPagination()
    paginated_users = paginator.paginate_queryset(users, request)

    serializer = CredSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)