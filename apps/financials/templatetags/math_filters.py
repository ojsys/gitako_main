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

@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        if value is None or arg is None:
            return 0
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        if value is None or arg is None:
            return 0
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        if value is None or arg is None or float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage of value relative to total"""
    try:
        if total is None or float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0