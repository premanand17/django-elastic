from django.shortcuts import render
from django.http.response import JsonResponse
from elastic.elastic_model import Elastic
from elastic.elastic_settings import ElasticSettings
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

fields = ["gene_symbol", "hgnc", "synonyms", "id",
          "dbxrefs.*", "attr.*", "featureloc.seqid"]


def search(request, query, search_db=ElasticSettings.indices_str()):
    ''' Renders a elastic results page based on the query '''
    elastic = Elastic.field_search_query(query, fields, 0, 20, db=search_db)
    return render(request, 'elastic/searchresults.html', elastic.get_result(),
                  content_type='text/html')


def range_overlap_search(request, src, start, stop, search_db=ElasticSettings.indices_str()):
    ''' Renders a elastic result page based on the src, start and stop '''
    elastic = Elastic.range_overlap_query(src, start, stop, db=search_db)
    context = elastic.get_result()
    context["chromosome"] = src
    context["start"] = start
    context["stop"] = stop
    return render(request, 'elastic/searchresults.html', context,
                  content_type='text/html')


''' AJAX QUERIES '''


def ajax_search(request, query, search_db, ajax):
    ''' Return count or paginated elastic result as a JSON '''
    if ajax == 'count':
        elastic = Elastic.field_search_query(query, fields, db=search_db)
        return JsonResponse(elastic.get_count())
    search_from = request.POST.get("from")
    size = request.POST.get("size")
    elastic = Elastic.field_search_query(query, fields, search_from, size, db=search_db)
    return JsonResponse(elastic.get_json_response())


def ajax_range_overlap_search(request, src, start, stop, search_db, ajax):
    ''' Return count or paginated range elastic result as a JSON '''
    if ajax == 'count':
        elastic = Elastic.range_overlap_query(src, start, stop, db=search_db)
        return JsonResponse(elastic.get_count())
    search_from = request.POST.get("from")
    size = request.POST.get("size")
    elastic = Elastic.range_overlap_query(src, start, stop, search_from, size, db=search_db)
    return JsonResponse(elastic.get_json_response())
