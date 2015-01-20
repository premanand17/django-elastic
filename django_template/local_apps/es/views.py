from django.shortcuts import render
from django.http import JsonResponse
import json, requests
#from django.views.decorators.cache import cache_page


def search(request):
    context = {}
    return render(request, 'search/elasticsearch.html', context)

def search2(request, query):
    
    data = {
            "query": {
                      "query_string": { "query": query }
                      }
            }
    response = requests.post('http://127.0.0.1:9200/dbsnp142/_search', data=json.dumps(data))
    #print (response.status_code)
    #print ( len(response.json()['hits']['hits']) )
    
    if(len(response.json()['hits']['hits']) < 1):
        context = {}
    else:
        context = response.json()['hits']['hits'][0]['_source']
    #print (context)
    return render(request, 'search/elasticsearch.html', context, content_type='text/html')

