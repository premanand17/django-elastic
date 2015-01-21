from django.shortcuts import render
from django.http import JsonResponse
import json, requests, re
#from django.views.decorators.cache import cache_page

def wildcard(request, query):
    query = query.replace("w", "*")
    data = { "query": { "wildcard" : { "ID" : query } } }  
    context = _getContext(data)
    return render(request, 'search/elasticsearch.html', context)

def search(request, query):
    data = { "query": { "match": { "ID": query } } }
    context = _getContext(data)
    return render(request, 'search/elasticsearch.html', context, content_type='text/html')

'''
Query the elasticsearch server for given search data and return the
context dictionary to pass to the template
'''
def _getContext(data):
    size = 20;
    response = requests.post('http://127.0.0.1:9200/dbsnp142/_search?size='+str(size), data=json.dumps(data))
    #print (response.json())
    #print ( len(response.json()['hits']['hits']) )
    context = {}
    content = []
    if(len(response.json()['hits']['hits']) >= 1):
        for hit in response.json()['hits']['hits']:
            #print(hit['_source']['INFO'])
            _addInfo(content, hit)
            content.append(hit['_source'])
            #print(hit['_source'])

    context["data"] = content
    context["total"] = response.json()['hits']['total']
    if(int(response.json()['hits']['total']) < size):
        context["size"] = response.json()['hits']['total']
    else:
        context["size"] = size
    return context;

'''
Split and add INFO tags and values
'''
def _addInfo(content, hit):
    infos = re.split(';', hit['_source']['INFO'])
    for info in infos:
        if "=" in info:
            parts = re.split('=', info)
            hit['_source'][parts[0]] = parts[1]
        else:
            hit['_source'][info] = ""
