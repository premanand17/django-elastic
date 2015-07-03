from elastic.search import Search, ElasticQuery
from elastic.tastypie.resources import ElasticObject
from elastic.query import Query, AndFilter
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response


class ElasticFilterBackend(OrderingFilter, DjangoFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filterable = getattr(view, 'filter_fields', [])
        filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])
        search_filters = self.build_filters(filters=filters)
        if search_filters is not None:
            q = ElasticQuery.filtered(Query.match_all(), search_filters)
        else:
            q = ElasticQuery(Query.match_all())
        s = Search(search_query=q, idx=getattr(view, 'idx'), size=5000)
        json_results = s.get_json_response()
        results = []
        for result in json_results['hits']['hits']:
            new_obj = ElasticObject(initial=result['_source'])
            new_obj.uuid = result['_id']
            results.append(new_obj)
        return results

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        and_filter = None
        for filter_expr, value in filters.items():
            filter_bits = filter_expr.split('__')
            field_name = filter_bits.pop(0)
            filter_type = 'exact'

            if len(filter_bits):
                filter_type = filter_bits.pop()

            if filter_type != 'exact':
                field_name = field_name + "." + filter_type

            q = Query.query_string(value, fields=[field_name]).query_wrap()
            if and_filter is None:
                and_filter = AndFilter(q)
            else:
                and_filter.extend(q)

        return and_filter


class ListElasticMixin(object):
    """ List a queryset. """
    filter_backends = [ElasticFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
