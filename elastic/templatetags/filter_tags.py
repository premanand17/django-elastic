''' Custom Template Tags '''
from django import template
from django.conf import settings
from elastic.result import Document
from elastic.elastic_settings import ElasticSettings

register = template.Library()


@register.filter
def doc_attr(doc, arg):
    ''' Gets attribute of an object dynamically from a string name '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    if arg not in doc.__dict__:
        return None
    return getattr(doc, arg)


@register.filter
def doc_keys(doc):
    ''' Gets the keys of the document object. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    return sorted(list(doc.__dict__.keys()))


@register.filter
def doc_highlight(doc):
    ''' Gets the highlighted section. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID

    html = ''
    if doc.highlight() is None:
        return ''
    for key, values in doc.highlight().items():
        html += '<strong>%s</strong>: ' % key
        for value in values:
            html += '%s<br/> ' % value
    return html


@register.filter
def doc_type(doc):
    ''' Gets the document type. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    return doc.type()


@register.filter
def doc_link(doc):
    ''' Gets the document details. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID

    return ElasticSettings.url() + '/' + doc.index() + '/' + doc.type() + \
        '/' + doc.doc_id() + '?routing=' + doc.doc_id()
