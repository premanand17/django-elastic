''' Custom Template Tags '''
from django import template
from django.conf import settings
from elastic.result import Document
from elastic.elastic_settings import ElasticSettings
import collections

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
def doc_attr_str(doc, arg):
    ''' Gets attribute of an object dynamically from a string name '''
    attr = doc_attr(doc, arg)
    if isinstance(attr, str):
        return attr
    elif isinstance(attr, list):
        return '; '.join(attr)
    else:
        return attr


@register.filter
def get_item(dictionary, key):
    ''' Get an item from the dictionary. '''
    return dictionary.get(key)


@register.filter
def doc_keys(doc):
    ''' Gets the keys of the document object. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    return sorted(list(doc.__dict__.keys()))


@register.filter
def doc_type(doc):
    ''' Gets the document type. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    return doc.type()


@register.filter
def doc_id(doc):
    ''' Gets the document ID. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID
    return doc.doc_id()


@register.filter
def doc_link(doc):
    ''' Gets the document details. '''
    if not isinstance(doc, Document):
        return settings.TEMPLATE_STRING_IF_INVALID

    return ElasticSettings.url() + '/' + doc.index() + '/' + doc.type() + \
        '/' + doc.doc_id() + '?routing=' + doc.doc_id()


@register.filter(name='sort')
def listsort(value):
    ''' Sort list and iterable arguments. '''
    if isinstance(value, list):
        try:
            new_list = list(value)
            new_list.sort()
            return new_list
        except TypeError:
            # sorting a list of dictionaries?
            if 'key' in value[0]:
                return sorted(value, key=lambda k: k['key'])
    elif isinstance(value, collections.Iterable):
        return sorted(value)
    return value

listsort.is_safe = True
