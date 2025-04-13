from celery import shared_task
from fcm_django.models import FCMDevice

@shared_task
def send_push_notification(user_id, title, message, data=None):
    """
    Send push notification to a user's devices
    """
    devices = FCMDevice.objects.filter(user_id=user_id, active=True)
    
    # Send to all user devices
    if devices.exists():
        result = devices.send_message(
            title=title,
            body=message,
            data=data or {},
            sound=True
        )
        return f"Notification sent to {devices.count()} devices"
    return "No devices found for user"

@shared_task
def send_bulk_notifications(user_ids, title, message, data=None):
    """
    Send push notifications to multiple users
    """
    devices = FCMDevice.objects.filter(user_id__in=user_ids, active=True)
    
    if devices.exists():
        result = devices.send_message(
            title=title,
            body=message,
            data=data or {},
            sound=True
        )
        return f"Notification sent to {devices.count()} devices"
    return "No devices found for users"