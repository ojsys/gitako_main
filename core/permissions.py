from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has an owner field and if the request user is the owner
        return hasattr(obj, 'owner') and obj.owner == request.user

class IsFarmOwner(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to access farm data.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has a farm field and if the request user is the farm owner
        if hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        return False