from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.core.urlresolvers import NoReverseMatch
import requests
from search.elastic_model import Elastic
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
    url = "%s%s" % (settings.SEARCH_ELASTIC_URL, path)
    requestor = getattr(requests, request.method.lower())
    proxy_resp = requestor(url, data=request.body, files=request.FILES)
    logger.warn('using reverse_proxy() in DEBUG mode ('+url+')')
    return HttpResponse(proxy_resp.content,
                        content_type=proxy_resp.headers.get('content-type'))


def search(request, query, search_db=settings.SEARCH_MARKERDB + ',' +
           settings.SEARCH_GENEDB + ',' + settings.SEARCH_REGIONDB):
    ''' Renders a search results page based on the query '''
    fields = ["gene_symbol", "hgnc", "synonyms", "id",
              "dbxrefs.*", "attr.*", "featureloc.seqid"]
    elastic = Elastic.field_search_query(query, fields, 0, 20, db=search_db)
    return render(request, 'search/searchresults.html', elastic.get_result(),
                  content_type='text/html')


def range_overlap_search(request, src, start, stop, search_db=settings.SEARCH_MARKERDB + ',' +
                         settings.SEARCH_GENEDB + ',' + settings.SEARCH_REGIONDB):
    ''' Renders a search result page based on the src, start and stop '''
    elastic = Elastic.range_overlap_query(src, start, stop, db=search_db)
    context = elastic.get_result()
    context["chromosome"] = src
    context["start"] = start
    context["stop"] = stop
    return render(request, 'search/searchresults.html', context,
                  content_type='text/html')
