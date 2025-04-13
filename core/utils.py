import uuid
import os
from django.utils.text import slugify

def generate_unique_slug(instance, field_name, new_slug=None):
    """
    Generate a unique slug for a model instance
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(getattr(instance, field_name))
    
    Model = instance.__class__
    qs_exists = Model.objects.filter(slug=slug).exists()
    
    if qs_exists:
        new_slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        return generate_unique_slug(instance, field_name, new_slug=new_slug)
    
    return slug

def get_file_path(instance, filename):
    """
    Generate a unique file path for uploaded files
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join(instance.__class__.__name__.lower(), filename)