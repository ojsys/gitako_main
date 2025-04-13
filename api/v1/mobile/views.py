from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class MobileConfigView(APIView):
    """
    Returns configuration settings for mobile apps
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Return app configuration for mobile clients
        return Response({
            'app_version': '1.0.0',
            'min_supported_version': '1.0.0',
            'force_update': False,
            'maintenance_mode': False,
            'features': {
                'marketplace_enabled': True,
                'recommendations_enabled': True,
                'weather_alerts_enabled': True,
            }
        })

class RegisterDeviceView(APIView):
    """
    Register a mobile device for push notifications
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        device_token = request.data.get('device_token')
        device_type = request.data.get('device_type')  # 'ios' or 'android'
        
        if not device_token or not device_type:
            return Response(
                {'error': 'device_token and device_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Logic to register device token with FCM
        # ...
        
        return Response({'status': 'device registered'})

class DataSyncView(APIView):
    """
    Synchronize data between mobile app and server
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Handle data synchronization from mobile clients
        # This would typically include handling offline changes
        
        last_sync = request.data.get('last_sync_timestamp')
        changes = request.data.get('changes', [])
        
        # Process changes from mobile client
        # ...
        
        # Return new data since last sync
        return Response({
            'sync_timestamp': '2023-11-15T12:00:00Z',
            'changes': []
        })