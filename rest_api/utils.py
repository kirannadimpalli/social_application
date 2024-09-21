from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        attrs['email'] = attrs['email'].lower()
        return super().validate(attrs)

class CustomTokenRefreshView(TokenRefreshView):
    pass

class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = CustomTokenObtainPairSerializer

    def get_throttles(self):
        self.throttle_scope = 'custom_token'  
        return super().get_throttles()
