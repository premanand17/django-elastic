from django.shortcuts import render
from django.http import JsonResponse
import json, requests
#from django.views.decorators.cache import cache_page

def wildcard(request, query):
    data = { "query": { "wildcard" : { "ID" : query+"*" } } }  
    context = _getContext(data)
    return render(request, 'search/elasticsearch.html', context)

def search(request, query):
    data = { "query": { "query_string": { "query": query } } }
    context = _getContext(data)
    return render(request, 'search/elasticsearch.html', context, content_type='text/html')

def _getContext(data):
    size = 20;
    response = requests.post('http://127.0.0.1:9200/dbsnp142/_search?size='+str(size), data=json.dumps(data))
    #print (response.json())
    #print ( len(response.json()['hits']['hits']) )
    context = {}
    content = []
    if(len(response.json()['hits']['hits']) >= 1):
        for hit in response.json()['hits']['hits']:
            content.append(hit['_source'])
    context["data"] = content
    context["total"] = response.json()['hits']['total']
    if(int(response.json()['hits']['total']) < size):
        context["size"] = response.json()['hits']['total']
    else:
        context["size"] = size
    return context;
