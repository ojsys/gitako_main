# financials/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Returns the absolute value of the argument."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0