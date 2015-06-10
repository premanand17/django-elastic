''' Generic resources (L{ElasticResource} and L{BaseGFFResource}) to
inherit from when setting up an index as a resource to provide a TastyPie RESTful
interface. '''
from tastypie import fields
from tastypie.resources import Resource
from elastic.search import Search, ElasticQuery
from tastypie.bundle import Bundle
from django.db.models.constants import LOOKUP_SEP
from tastypie.exceptions import InvalidFilterError, NotFound
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from elastic.query import Query, AndFilter


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


class ElasticResource(Resource):
    ''' Override methods to define an Elastic index as a TastyPie resource.'''

    def _client(self, q=None):
        ''' Get the Elastic client. '''
        if self._meta.max_limit is None:
            max_limit = 2000000
        else:
            max_limit = self._meta.max_limit
        return Search(search_query=q, idx=self._meta.resource_name, size=max_limit)

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
        if hasattr(self, 'search_filters') and self.search_filters is not None:
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
        r = self._client(q).get_json_response()['hits']['hits']
        if len(r) <= 0:
            raise NotFound("Couldn't find an instance which matched id='%s'." % kwargs['pk'])

        new_obj = ElasticObject(initial=r[0]['_source'])
        new_obj.uuid = r[0]['_id']
        return new_obj

    def obj_create(self, bundle, **kwargs):
        pass

    def obj_update(self, bundle, **kwargs):
        pass

    def obj_delete_list(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        pass

    def rollback(self, bundles):
        pass

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        and_filter = None
        for filter_expr, value in filters.items():
            filter_bits = filter_expr.split(LOOKUP_SEP)
            field_name = filter_bits.pop(0)
            filter_type = 'exact'

            if field_name not in self._meta.filtering:
                continue
            if len(filter_bits):
                filter_type = filter_bits.pop()

            self.check_filtering(field_name, filter_type)

            if filter_type != 'exact':
                field_name = field_name + "." + filter_type

            q = Query.query_string(value, fields=[field_name]).query_wrap()
            if and_filter is None:
                and_filter = AndFilter(q)
            else:
                and_filter.extend(q)

        return and_filter

    def check_filtering(self, field_name, filter_type='exact'):
        """
        Based on tastypie.resources.BaseModelResource.check_filtering().
        Given a field name and an optional filter type determine if a field
        can be filtered on.
        If a filter does not meet the needed conditions, it should raise an
        ``InvalidFilterError``.
        If the filter meets the conditions, a list of attribute names (not
        field names) will be returned.
        """
        if field_name not in self._meta.filtering:
            raise InvalidFilterError("The '%s' field does not allow filtering." % field_name)

        # Check to see if it's an allowed lookup type.
        if not self._meta.filtering[field_name] in (ALL, ALL_WITH_RELATIONS):
            # Must be an explicit whitelist.
            if filter_type not in self._meta.filtering[field_name]:
                raise InvalidFilterError("'%s' is not an allowed filter on the '%s' field." % (filter_type, field_name))

        if self.fields[field_name].attribute is None:
            raise InvalidFilterError("The '%s' field has no 'attribute' for searching with." % field_name)
        return [self.fields[field_name].attribute]


class BaseGFFResource(ElasticResource):
    ''' Generic GFF resource. '''
    # define the fields
    seqid = fields.CharField(attribute='seqid', help_text='Sequence identifier')
    source = fields.CharField(attribute='source', help_text='Software/algorithm that generated the feature')
    type = fields.CharField(attribute='type', help_text='Type of feature')
    start = fields.IntegerField(attribute='start', help_text='Start coordinate of the feature')
    end = fields.IntegerField(attribute='end', help_text='End coordinate of the feature')
    score = fields.CharField(attribute='score', help_text='Score of the feature')
    strand = fields.CharField(attribute='strand', help_text='Strand of the feature')
    phase = fields.CharField(attribute='phase', help_text='Where feature begins with reference to reading frame')
    attr = fields.DictField(attribute='attr', help_text='List of feature attributes')
