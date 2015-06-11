from django.shortcuts import render
from django.http.response import JsonResponse
from elastic.search import Search, ElasticQuery
from elastic.elastic_settings import ElasticSettings
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from elastic.query import Query
from elastic.aggs import Agg, Aggs

# Get an instance of a logger
logger = logging.getLogger(__name__)

fields = ["gene_symbol", "hgnc", "synonyms", "id^2",
          "dbxrefs.*", "attr.*", "featureloc.seqid",
          "rscurrent", "rslow", "rshigh"]


def _add_diseases():
    ''' Add diseases dictionary to a context '''
    query = ElasticQuery(Query.match_all())
    elastic_disease = Search(search_query=query, size=100, idx='disease')
    return elastic_disease.get_json_response()['hits']['hits']


def _categories(idx):
    idxs = idx.split(",")
    idx_types = {}
    for this_idx in idxs:
        if this_idx+'/marker' == ElasticSettings.idx('MARKER', 'MARKER'):
            stype = {'type': 'Marker',
                     'categories': ['synonymous', 'non-synonymous'],
                     'search': ['in LD of selected']}
        elif this_idx == ElasticSettings.idx('REGION'):
            stype = {'type': 'Region'}
        elif this_idx == ElasticSettings.idx('GENE'):
            stype = {'type': 'Gene', 'categories': ['protein coding', 'non-coding', 'pseudogene']}
        else:
            stype = {'type': 'Other'}
        idx_types[this_idx] = stype
    return idx_types


@ensure_csrf_cookie
def search(request, query, search_idx=ElasticSettings.indices_str()):
    ''' Renders a elastic results page based on the query '''

    aggs = Aggs(Agg("categories", "terms", {"field": "_type", "size": 0}))
    elastic = Search.field_search_query(query, aggs=aggs, fields=fields,
                                        search_from=0, size=20, idx=search_idx)
    result = elastic.search()
    context = {}
    context['diseases'] = _add_diseases()
    context['total'] = result.hits_total
    context['db'] = result.idx
    context['size'] = result.size
    context['query'] = result.query
    context["idxs"] = _categories(result.idx)
    return render(request, 'elastic/searchresults.html', context,
                  content_type='text/html')


@ensure_csrf_cookie
def range_overlap_search(request, src, start, stop, search_idx=ElasticSettings.indices_str()):
    ''' Renders a elastic result page based on the src, start and stop '''
    elastic = Search.range_overlap_query(src, start, stop, idx=search_idx)

    result = elastic.search()
    context = {}
    context['diseases'] = _add_diseases()
    context['total'] = result.hits_total
    context['db'] = result.idx
    context['size'] = result.size
    context['query'] = result.query
    context["idxs"] = _categories(result.idx)
    context["chromosome"] = src
    context["start"] = start
    context["stop"] = stop
    return render(request, 'elastic/searchresults.html', context,
                  content_type='text/html')


''' AJAX QUERIES '''


def ajax_search(request, query, search_idx, ajax):
    ''' Return count or paginated elastic result as a JSON '''
    if ajax == 'count':
        elastic = Search.field_search_query(query, fields=fields, idx=search_idx)
        return JsonResponse(elastic.get_count())
    search_from = request.POST.get("from")
    size = request.POST.get("size")
    elastic = Search.field_search_query(query, fields=fields, search_from=search_from,
                                        size=size, idx=search_idx)
    return JsonResponse(elastic.get_json_response())


def ajax_range_overlap_search(request, src, start, stop, search_idx, ajax):
    ''' Return count or paginated range elastic result as a JSON '''
    if ajax == 'count':
        elastic = Search.range_overlap_query(src, start, stop, idx=search_idx)
        return JsonResponse(elastic.get_count())
    search_from = request.POST.get("from")
    size = request.POST.get("size")
    elastic = Search.range_overlap_query(src, start, stop, search_from=search_from,
                                         size=size, idx=search_idx)
    return JsonResponse(elastic.get_json_response())
