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

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Add a CSS class to a form field
    Usage: {{ field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={
        "class": f"{field.css_classes()} {css_class}"
    })