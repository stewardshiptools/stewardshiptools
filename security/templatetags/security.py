from django import template
from security.utils import get_security_level_or_default_from_object, get_security_level_or_default_value_from_object

register = template.Library()


@register.filter
def security_level_or_default(obj):
    return get_security_level_or_default_from_object(obj)


@register.filter
def security_level_or_default_value(obj):
    return get_security_level_or_default_value_from_object(obj)
