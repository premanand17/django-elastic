from django.shortcuts import render
from django.http.response import JsonResponse
from elastic.elastic_model import Search
from elastic.elastic_settings import ElasticSettings
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

fields = ["gene_symbol", "hgnc", "synonyms", "id",
          "dbxrefs.*", "attr.*", "featureloc.seqid"]


def search(request, query, search_idx=ElasticSettings.indices_str()):
    ''' Renders a elastic results page based on the query '''
    elastic = Search.field_search_query(query, fields, 0, 20, idx=search_idx)
    return render(request, 'elastic/searchresults.html', elastic.get_result(),
                  content_type='text/html')


def range_overlap_search(request, src, start, stop, search_idx=ElasticSettings.indices_str()):
    ''' Renders a elastic result page based on the src, start and stop '''
    elastic = Search.range_overlap_query(src, start, stop, idx=search_idx)
    context = elastic.get_result()
    context["chromosome"] = src
    context["start"] = start
    context["stop"] = stop
    return render(request, 'elastic/searchresults.html', context,
                  content_type='text/html')


''' AJAX QUERIES '''


def ajax_search(request, query, search_idx, ajax):
    ''' Return count or paginated elastic result as a JSON '''
    if ajax == 'count':
        elastic = Search.field_search_query(query, fields, idx=search_idx)
        return JsonResponse(elastic.get_count())
    search_from = request.POST.get("from")
    size = request.POST.get("size")
    elastic = Search.field_search_query(query, fields, search_from, size, idx=search_idx)
    return JsonResponse(elastic.get_json_response())


def ajax_range_overlap_search(request, src, start, stop, search_idx, ajax):
    ''' Return count or paginated range elastic result as a JSON '''
    if ajax == 'count':
        elastic = Search.range_overlap_query(src, start, stop, idx=search_idx)
        return JsonResponse(elastic.get_count())
    search_from = request.POST.get("from")
    size = request.POST.get("size")
    elastic = Search.range_overlap_query(src, start, stop, search_from, size, idx=search_idx)
    return JsonResponse(elastic.get_json_response())
