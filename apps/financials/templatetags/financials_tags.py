from django import template

register = template.Library()

@register.filter
def currency(value):
    """Format a value as currency"""
    try:
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def percentage(value):
    """Format a value as percentage"""
    try:
        return "{:,.1f}%".format(float(value) * 100)
    except (ValueError, TypeError):
        return "0.0%"

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0