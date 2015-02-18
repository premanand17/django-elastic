from django import template
from django.conf import settings

register = template.Library()
VISIBLE_SETTINGS = ["MARKERDB"]


# settings value
@register.simple_tag
def settings_value(name):
    if name in VISIBLE_SETTINGS:
        return getattr(settings, name, "")
