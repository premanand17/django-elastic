# We need a generic object to shove data in/get data from.
# Riak generally just tosses around dictionaries, so we'll lightly
# wrap that.
from tastypie.resources import Resource
from tastypie import fields
from tastypie.bundle import Bundle
from elastic.elastic_model import Search, AndFilter, Query, ElasticQuery
from tastypie.constants import ALL


class GffObject(object):
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
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.
    seqid = fields.CharField(attribute='seqid')
    source = fields.CharField(attribute='source')
    type = fields.CharField(attribute='type')
    start = fields.IntegerField(attribute='start')
    end = fields.IntegerField(attribute='end')
    score = fields.CharField(attribute='score')
    phase = fields.CharField(attribute='phase')
    attr = fields.DictField(attribute='attr')

    class Meta:
        resource_name = 'gff'
        object_class = GffObject
        filtering = {
            'attr': ALL,
            'seqid': ALL,
        }

    # Specific to this resource, just to get the needed Riak bits.
    def _client(self, q=None):
        return Search(search_query=q, idx="grch37_75_genes", size=20000000)

    def _bucket(self):
        client = self._client()
        # Note that we're hard-coding the bucket to use. Fine for
        # example purposes, but you'll want to abstract this.
#         return client.bucket('messages')
        return client

    # The following methods will need overriding regardless of your
    # data source.
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.uuid
        else:
            kwargs['pk'] = bundle_or_obj.uuid

        return kwargs

    def get_object_list(self, request):
        ''' Gets the result list. '''
        print("XXXXX get_object_list")

        if self.search_filters is not None:
            q = ElasticQuery.filtered(Query.match_all(), self.search_filters)
        else:
            q = ElasticQuery(Query.match_all())

        query = self._client(q).get_json_response()
        results = []

        for result in query['hits']['hits']:
            new_obj = GffObject(initial=result['_source'])
            new_obj.uuid = result['_id']
            results.append(new_obj)
        return results

    def obj_get_list(self, bundle, **kwargs):
        # Filtering disabled for brevity...
        print("XXXXXxxx obj_get_list")
        filters = {}
        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()
        # Update with the provided kwargs.
        filters.update(kwargs)
        self.search_filters = self.build_filters(filters=filters)

        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        print("XXXXX obj_get")
        bucket = self._bucket()
        gff = bucket.get(kwargs['pk'])
        return GffObject(initial=gff.get_data())

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        and_filter = None
        for name, value in filters.items():
            if name not in self._meta.filtering:
                continue
            q = Query.term(name, value)
            if and_filter is None:
                and_filter = AndFilter(q)
            else:
                and_filter.extend(q)
            print(name)
        return and_filter
