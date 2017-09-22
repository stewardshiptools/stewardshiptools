from django import template

from sanitizer.utils.sanitizer import sanitize as san

register = template.Library()


@register.assignment_tag()
def sanitize(text, replace_char='_', obj=None):
    return san(text, replace_char, obj)
