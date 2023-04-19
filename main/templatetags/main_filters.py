from django import template

register = template.Library()

@register.filter
def modulus(value, arg):
    """Returns value mod arg"""
    return value % arg