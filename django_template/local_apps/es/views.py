from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.core.urlresolvers import NoReverseMatch
import json
import requests
import re


@csrf_exempt
def reverse_proxy(request):
    '''
    Reverse proxy for elasticsearch on different port.
    Based on https://gist.github.com/JustinTArthur/5710254.
    To be used ONLY in DEBUG mode.
    '''
    if(not settings.DEBUG):
        raise NoReverseMatch
    path = request.get_full_path()
    url = "%s%s" % (settings.ELASTICSEARCH_URL, path)
    requestor = getattr(requests, request.method.lower())
    proxy_resp = requestor(url, data=request.body, files=request.FILES)
    return HttpResponse(proxy_resp.content,
                        content_type=proxy_resp.headers.get('content-type'))


def wildcard(request, query):
    query = query.replace("w", "*")
    data = {"query": {"wildcard": {"ID": query}}}
    context = elastic_search(data)
    return render(request, 'search/searchresults.html', context)


def search(request, query):
    data = {"query": {"match": {"ID": query}}}
    context = elastic_search(data)
    return render(request, 'search/searchresults.html', context,
                  content_type='text/html')


def range_search(request, src, start, stop):

    must = [{"match": {"SRC": src.replace('chr', '')}},
            {"range": {"POS": {"gte": start, "lte": stop, "boost": 2.0}}}]
    query = {"bool": {"must": must}}
    data = {"query": query}
    context = elastic_search(data)
    context["chromosome"] = src
    context["start"] = start
    context["stop"] = stop
    return render(request, 'search/searchresults.html', context,
                  content_type='text/html')


def elastic_search(data, search_from=0):
    '''
    Query the elasticsearch server for given search data and return the
    context dictionary to pass to the template
    '''
    size = 20
    url = (settings.ELASTICSEARCH_URL + '/' +
           settings.MARKERDB + '/' +
           '_search?size=' + str(size) +
           '&from='+str(search_from))
    response = requests.post(url, data=json.dumps(data))

    context = {"query": data}
    context["db"] = settings.MARKERDB
    content = []
    if(len(response.json()['hits']['hits']) >= 1):
        for hit in response.json()['hits']['hits']:
            #print(hit['_source']['REF']) @IgnorePep8
            _addInfo(content, hit)
            content.append(hit['_source'])
            #print(hit['_source']) @IgnorePep8

    context["data"] = content
    context["total"] = response.json()['hits']['total']
    if(int(response.json()['hits']['total']) < size):
        context["size"] = response.json()['hits']['total']
    else:
        context["size"] = size
    return context


def _addInfo(content, hit):
    '''
    Split and add INFO tags and values
    '''
    infos = re.split(';', hit['_source']['INFO'])
    for info in infos:
        if "=" in info:
            parts = re.split('=', info)
            if parts[0] not in hit['_source']:
                hit['_source'][parts[0]] = parts[1]
        else:
            if info not in hit['_source']:
                hit['_source'][info] = ""
