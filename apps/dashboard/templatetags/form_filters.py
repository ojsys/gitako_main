from django import template

register = template.Library()

@register.filter(name='attr')
def attr(field, attr_string):
    """
    Add attributes to form fields
    Usage: {{ field|attr:"class:form-control" }}
    """
    attrs = {}
    parts = attr_string.split(':')
    if len(parts) == 2:
        attrs[parts[0]] = parts[1]
    
    return field.as_widget(attrs=attrs)