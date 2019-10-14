from django import template
from django.utils.html import escape

register = template.Library()


@register.filter
def has_error(errors, input_name):
    if input_name in errors:
        return True
    return False


@register.filter
def get_error(errors, input_name):
    if input_name in errors:
        return errors[input_name].as_text()
