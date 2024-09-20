from rest_framework import serializers
from .models import UserDetails
from .models import CustomUser




class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = '__all__'


class CredSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
