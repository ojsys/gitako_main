import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api.requests')

class RequestLogMiddleware(MiddlewareMixin):
    """Middleware to log API requests and responses"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        # The issue is here - trying to access request.body after it's been consumed
        if request.method != 'GET':
            # Don't try to access request.body directly
            # Instead, check if the content type is multipart/form-data
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'multipart/form-data' in content_type:
                # Skip processing for multipart form data (file uploads)
                return response
                
            # For other requests, you might want to try/except the body access
            try:
                # Only try to access body if it hasn't been consumed
                if hasattr(request, '_body'):
                    # Body has already been accessed, don't try again
                    pass
                else:
                    # Your original logic here that used request.body
                    pass
            except Exception:
                # If there's an error accessing the body, just continue
                pass
        
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': round(duration * 1000, 2),  # Convert to milliseconds
                'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            }
            
            # Log request data for non-GET requests
            if request.method != 'GET' and request.body:
                try:
                    log_data['request_body'] = json.loads(request.body)
                except json.JSONDecodeError:
                    log_data['request_body'] = str(request.body)
            
            logger.info(f"API Request: {json.dumps(log_data)}")
            
        return response