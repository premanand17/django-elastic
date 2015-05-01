from tastypie.resources import Resource
from tastypie import fields
from tastypie.bundle import Bundle
from elastic.elastic_model import Search, AndFilter, Query, ElasticQuery
from tastypie.constants import ALL
from django.db.models.constants import LOOKUP_SEP


class ElasticObject(object):
    ''' Generic object to hold Elastic dictionaries. '''
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class GFFResource(Resource):
    # define the fields
    seqid = fields.CharField(attribute='seqid')
    source = fields.CharField(attribute='source')
    type = fields.CharField(attribute='type')
    start = fields.IntegerField(attribute='start')
    end = fields.IntegerField(attribute='end')
    score = fields.CharField(attribute='score')
    phase = fields.CharField(attribute='phase')
    attr = fields.DictField(attribute='attr')

    class Meta:
        resource_name = 'grch37_75_genes'
        object_class = ElasticObject
        filtering = {
            'attr': ALL,
            'seqid': ALL,
        }

    def _client(self, q=None):
        ''' Get the Elastic client. '''
        return Search(search_query=q, idx=self._meta.resource_name, size=20000000)

    # overriding the following methods
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.uuid
        else:
            kwargs['pk'] = bundle_or_obj.uuid
        return kwargs

    def get_object_list(self, request):
        ''' Gets the result list. '''
        if self.search_filters is not None:
            q = ElasticQuery.filtered(Query.match_all(), self.search_filters)
        else:
            q = ElasticQuery(Query.match_all())

        json_results = self._client(q).get_json_response()
        results = []

        for result in json_results['hits']['hits']:
            new_obj = ElasticObject(initial=result['_source'])
            new_obj.uuid = result['_id']
            results.append(new_obj)
        return results

    def obj_get_list(self, bundle, **kwargs):
        filters = {}
        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()
        # Update with the provided kwargs.
        filters.update(kwargs)
        self.search_filters = self.build_filters(filters=filters)

        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        ''' Used to get by Elastic _uid. '''
        q = ElasticQuery(Query.ids(kwargs['pk']))
        result = self._client(q).get_json_response()['hits']['hits'][0]
        new_obj = ElasticObject(initial=result['_source'])
        new_obj.uuid = result['_id']
        return new_obj

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        and_filter = None
        for filter_expr, value in filters.items():
            filter_bits = filter_expr.split(LOOKUP_SEP)
            field_name = filter_bits.pop(0)

            if field_name not in self._meta.filtering:
                continue

            if len(filter_bits):
                filter_type = filter_bits.pop()
                field_name = field_name + "." + filter_type

            q = Query.query_string(value, fields=[field_name]).query_wrap()
            if and_filter is None:
                and_filter = AndFilter(q)
            else:
                and_filter.extend(q)

        return and_filter
