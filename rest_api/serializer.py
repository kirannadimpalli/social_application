from rest_framework import serializers
from .models import CustomUser, FriendRequest



class CredSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'description', 'mobile_number', 'is_active', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        data['email'] = data['email'].lower()
        return data

    def create(self, validated_data):
        breakpoint()
        user = CustomUser(
            email=validated_data['email'],
            name=validated_data.get('name'),
            description=validated_data.get('description'),
            mobile_number=validated_data.get('mobile_number'),
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False)  
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receiver = CredSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'created_at', 'status', 'rejected_at']

    def get_sender(self, obj):
        if obj.status == 'accepted':
            return CredSerializer(obj.sender).data
        return {
            'id': obj.sender.id,
            'email': obj.sender.email 
        }

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser 
        fields = ['email', 'name', 'mobile_number'] 