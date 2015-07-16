''' Custom Template Tags '''
from django import template
from django.conf import settings
from elastic.result import Document

register = template.Library()


@register.filter
def doc_attr(doc, arg):
    ''' Gets attribute of an object dynamically from a string name '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    if arg not in doc.__dict__:
        return None
    return getattr(doc, arg)
