from elastic.search import Search, ElasticQuery
from elastic.tastypie.resources import ElasticObject
from elastic.query import Query, AndFilter
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.http.response import Http404


class ElasticLimitOffsetPagination(LimitOffsetPagination):

    def paginate_queryset(self, queryset, request, view=None):
        if not hasattr(view, 'es_count'):
            return super().paginate_queryset(queryset, request, view)

        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.count = view.es_count
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        return queryset


class ElasticFilterBackend(OrderingFilter, DjangoFilterBackend):

    def filter_queryset(self, request, queryset, view):
        paginator = view.paginator
        q_size = paginator.get_limit(request)
        q_from = view.paginator.get_offset(request)

        filterable = getattr(view, 'filter_fields', [])
        filters = dict([(k, v) for k, v in request.GET.items() if k in filterable])
        search_filters = self.build_filters(filters=filters)
        if search_filters is not None:
            q = ElasticQuery.filtered(Query.match_all(), search_filters)
        else:
            q = ElasticQuery(Query.match_all())
        s = Search(search_query=q, idx=getattr(view, 'idx'), size=q_size, search_from=q_from)
        json_results = s.get_json_response()
        results = []
        for result in json_results['hits']['hits']:
            new_obj = ElasticObject(initial=result['_source'])
            new_obj.uuid = result['_id']
            results.append(new_obj)
        view.es_count = json_results['hits']['total']

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
    ''' List a queryset. '''
    filter_backends = [ElasticFilterBackend, ]

    def get_queryset(self):
        return None

    def list(self, request, *args, **kwargs):
        ''' Retrieve a list of documents. '''
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        ''' Retrieve a document instance. '''
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        q = ElasticQuery(Query.ids(self.kwargs[self.lookup_field]))
        s = Search(search_query=q, idx=getattr(self, 'idx'))
        try:
            result = s.get_json_response()['hits']['hits'][0]
            obj = ElasticObject(initial=result['_source'])
            obj.uuid = result['_id']

            # May raise a permission denied
            self.check_object_permissions(self.request, obj)
            return obj
        except (TypeError, ValueError, IndexError):
            raise Http404
