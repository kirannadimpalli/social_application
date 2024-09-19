from rest_framework import serializers
from .models import UserDetails
from django.contrib.auth.models import User




class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = '__all__'


class CredSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User 
        fields = ['id', 'username', 'password', 'email']
