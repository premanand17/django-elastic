from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.core.urlresolvers import NoReverseMatch
import requests
from es.elastic_model import Elastic


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


def search(request, query, search_db=settings.MARKERDB + ',' +
           settings.GENEDB + ',' + settings.REGIONDB):
    ''' Renders a search results page based on the query '''
    fields = ["gene_symbol", "hgnc", "synonyms", "id",
              "dbxrefs.*", "attr.*", "featureloc.seqid"]
    data = {"query": {"query_string": {"query": query, "fields": fields}}}
    elastic = Elastic(data, 0, 20, db=search_db)
    return render(request, 'search/searchresults.html', elastic.get_result(),
                  content_type='text/html')


def range_search(request, src, start, stop, search_db=settings.MARKERDB + ',' +
                 settings.GENEDB + ',' + settings.REGIONDB):
    ''' Renders a search result page based on the src, start and stop '''

    must = [{"match": {"seqid": src}},
            {"range": {"start": {"gte": start, "boost": 2.0}}},
            {"range": {"end": {"lte": stop, "boost": 2.0}}}]
    query = {"bool": {"must": must}}
    data = {"query": query}
    elastic = Elastic(data, db=search_db)
    context = elastic.get_result()
    context["chromosome"] = src
    context["start"] = start
    context["stop"] = stop
    return render(request, 'search/searchresults.html', context,
                  content_type='text/html')


def filtered_range_search(request, src, start, stop, db):
    '''
    Pass the range parameters to the range_search routine.
    '''
    return range_search(request, src, start, stop, db)


def filtered_search(request, query, db):
    '''
    Pass the search parameters to the regular search routine
    '''
    return search(request, query, db)
