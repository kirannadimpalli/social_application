from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CustomTokenRefreshView(TokenRefreshView):
    pass

class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_throttles(self):
        self.throttle_scope = 'custom_token'  
        return super().get_throttles()
