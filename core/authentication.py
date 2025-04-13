from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from datetime import timedelta

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication with expiration
    """
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        
        # Check if token has expired (30 days)
        if token.created < timezone.now() - timedelta(days=30):
            token.delete()
            raise AuthenticationFailed('Token has expired')
            
        return user, token