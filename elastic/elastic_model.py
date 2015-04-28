import json
import requests
import logging
from elastic.elastic_settings import ElasticSettings

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Search:
    ''' Used to run Elastic searches and return results or mappings. '''

    def __init__(self, search_query=None, search_from=0, size=20, idx=ElasticSettings.idx('DEFAULT')):
        ''' Query the elastic server for given elastic query '''
        self.url = (ElasticSettings.url() + '/' + idx + '/_search?size=' + str(size) +
                    '&from='+str(search_from))
        if search_query is not None:
            if not isinstance(search_query, ElasticQuery):
                raise QueryError("not an ElasticQuery")
            self.query = search_query.query
        self.size = size
        self.idx = idx

    @classmethod
    def index_exists(cls, idx, url=ElasticSettings.url()):
        ''' Check if an index exists. '''
        url += '/' + idx
        response = requests.get(url)
        if "error" in response.json():
            return False
        return True

    @classmethod
    def range_overlap_query(cls, seqid, start_range, end_range,
                            search_from=0, size=20, idx=ElasticSettings.idx('DEFAULT'),
                            field_list=None):
        ''' Constructs a range overlap query '''
        query_bool = BoolQuery(must_arr=[RangeQuery("start", lte=start_range),
                                         RangeQuery("end", gte=end_range)])
        or_filter = OrFilter(RangeQuery("start", gte=start_range, lte=end_range))
        or_filter.extend(RangeQuery("end", gte=start_range, lte=end_range)) \
                 .extend(query_bool)
        query = ElasticQuery.filtered(Query.term("seqid", seqid), or_filter, field_list)
        return cls(query, search_from, size, idx)

    @classmethod
    def field_search_query(cls, query_term, fields=None,
                           search_from=0, size=20, idx=ElasticSettings.idx('DEFAULT')):
        ''' Constructs a field elastic query '''
        query = ElasticQuery.query_string(query_term, fields=fields)
        return cls(query, search_from, size, idx)

    def get_mapping(self, mapping_type=None):
        ''' Return the mappings for an index. '''
        self.mapping_url = (ElasticSettings.url() + '/' + self.idx + '/_mapping')
        if mapping_type is not None:
            self.mapping_url += '/'+mapping_type
        response = requests.get(self.mapping_url)
        if response.status_code != 200:
            return json.dumps({"error": response.status_code})
        return response.json()

    def get_count(self):
        ''' Return the elastic count for a query result '''
        url = ElasticSettings.url() + '/' + self.idx + '/_count?'
        data = {}
        if hasattr(self, 'query'):
            data = json.dumps(self.query)
        response = requests.post(url, data=data)
        return response.json()

    def get_json_response(self):
        ''' Return the elastic json response '''
        response = requests.post(self.url, data=json.dumps(self.query))
        logger.debug("curl '" + self.url + "&pretty' -d '" + json.dumps(self.query) + "'")
        if response.status_code != 200:
            logger.warn("Error: elastic response 200:" + self.url)
        return response.json()

    def get_result(self):
        ''' Return the elastic context result '''
        json_response = self.get_json_response()
        context = {"query": self.query}
        c_dbs = {}
        dbs = self.idx.split(",")
        for this_db in dbs:
            stype = "Gene"
            if "snp" in this_db:
                stype = "Marker"
            if "region" in this_db:
                stype = "Region"
            c_dbs[this_db] = stype
        context["dbs"] = c_dbs
        context["db"] = self.idx

        content = []
        if(len(json_response['hits']['hits']) >= 1):
            for hit in json_response['hits']['hits']:
                hit['_source']['idx_type'] = hit['_type']
                hit['_source']['idx_id'] = hit['_id']
                content.append(hit['_source'])

        context["data"] = content
        context["total"] = json_response['hits']['total']
        if(int(json_response['hits']['total']) < self.size):
            context["size"] = json_response['hits']['total']
        else:
            context["size"] = self.size
        return context


class Query:
    ''' http://www.elastic.co/guide/en/elasticsearch/reference/1.5/query-dsl-queries.html '''
    def __init__(self, query):
        self.query = query

    STRING_OPTS = ["fields", "default_field", "default_operator",
                   "analyzer", "allow_leading_wildcard", "lowercase_expanded_terms",
                   "enable_position_increments", "fuzzy_max_expansions", "fuzzy_prefix_length",
                   "phrase_slop", "boost", "analyze_wildcard", "auto_generate_phrase_queries",
                   "max_determinized_states", "minimum_should_match", "lenient", "time_zone"]

    @classmethod
    def match_all(cls):
        ''' Factory method for Match All Query '''
        return cls({"match_all": {}})

    @classmethod
    def term(cls, name, value, boost=None):
        ''' Factory method for Term Query '''
        if boost is None:
            return cls({"term": {name: value}})
        return cls({"term": {name: {"value": value, "boost": boost}}})

    @classmethod
    def terms(cls, name, arr, minimum_should_match=1):
        ''' Factory method for Terms Query '''
        if minimum_should_match != 0:
            query = {"terms": {name: arr, "minimum_should_match": minimum_should_match}}
        else:
            query = {"terms": {name: arr}}
        return cls(query)

    @classmethod
    def match(cls, match_id, match_str):
        ''' Factory method for Basic match query '''
        return cls({"match": {match_id: match_str}})

    @classmethod
    def query_string(cls, query_term, **kwargs):
        ''' Factory method for String Query.
        Simple wildcards can be used with the fields supplied
        (e.g. "fields" : ["city.*"].) '''
        query = {"query_string": {"query": query_term}}

        for key, value in kwargs.items():
            if key not in Query.STRING_OPTS:
                raise QueryError("option "+key+" unrecognised as a String Query option")
            query["query_string"][key] = value
        return cls(query)

    @classmethod
    def is_array_query(cls, arr):
        ''' Evaluate if array contents are Query objects. '''
        for e in arr:
            if not isinstance(e, Query):
                raise QueryError("not a Query")
        return True

    @classmethod
    def query_to_str_array(cls, arr):
        ''' Return a str array from a query array. '''
        str_arr = []
        [str_arr.append(q.query) for q in arr]
        return str_arr


class ElasticQuery(Query):
    ''' Utility to assist in constructing Elastic queries. '''

    def __init__(self, query, sources=None, highlight=None):
        ''' Query the elastic server for given elastic query. '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.query = {"query": query.query}
        if sources is not None:
            self.query["_source"] = sources
        if highlight is not None:
            if not isinstance(highlight, Highlight):
                raise QueryError("not a Highlight")
            self.query.update(highlight.highlight)

    @classmethod
    def bool(cls, query_bool, sources=None, highlight=None):
        ''' Factory method for creating elastic Bool Query. '''
        if not isinstance(query_bool, BoolQuery):
            raise QueryError("not a BoolQuery")
        return cls(query_bool, sources, highlight)

    @classmethod
    def filtered_bool(cls, query_match, query_bool, sources=None, highlight=None):
        ''' Factory method for creating elastic filtered query with Bool filter. '''
        if not isinstance(query_bool, BoolQuery):
            raise QueryError("not a BoolQuery")
        return ElasticQuery.filtered(query_match, Filter(query_bool), sources, highlight)

    @classmethod
    def filtered(cls, query_match, query_filter, sources=None, highlight=None):
        ''' Factory method for creating elastic Filtered Query. '''
        query = FilteredQuery(query_match, query_filter)
        return cls(query, sources, highlight)

    @classmethod
    def query_string(cls, query_term, sources=None, highlight=None, **string_opts):
        ''' Factory method for creating elastic Query String Query '''
        query = Query.query_string(query_term, **string_opts)
        return cls(query, sources, highlight)

    @classmethod
    def query_match(cls, match_id, match_str, sources=None, highlight=None):
        ''' Factory method for creating elastic Match Query. '''
        query = Query.match(match_id, match_str)
        return cls(query, sources, highlight)


class FilteredQuery(Query):
    ''' Filtered Query - used to combine a query and a filter. '''
    def __init__(self, query, query_filter):
        ''' Bool query '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        if not isinstance(query_filter, Filter):
            raise QueryError("not a Filter")
        self.query = {"filtered": {"query": query.query}}
        self.query["filtered"].update(query_filter.filter)


class BoolQuery(Query):
    ''' Bool Query - a query that matches documents matching boolean
    combinations of other queries'''
    def __init__(self, must_arr=None, must_not_arr=None, should_arr=None):
        ''' Bool query '''
        self.query = {"bool": {}}
        if must_arr is not None:
            self.must(must_arr)
        if must_not_arr is not None:
            self.must_not(must_not_arr)
        if should_arr is not None:
            self.should(should_arr)

    def must(self, must_arr):
        return self._update("must", must_arr)

    def must_not(self, must_not_arr):
        return self._update("must_not", must_not_arr)

    def should(self, should_arr):
        return self._update("should", should_arr)

    def _update(self, name, qarr):
        if not isinstance(qarr, list):
            qarr = [qarr]

        Query.is_array_query(qarr)
        arr = Query.query_to_str_array(qarr)
        if name in self.query["bool"]:
            self.query["bool"][name].extend(arr)
        else:
            self.query["bool"][name] = arr
        return self


class RangeQuery(Query):
    ''' Range Query - matches documents with fields that have terms
    within a certain range.'''
    def __init__(self, name, gt=None, lt=None, gte=None, lte=None, boost=None):
        ''' Bool query '''
        self.query = {"range": {name: {}}}
        if gt is not None:
            self.query["range"][name]["gt"] = gt
        if lt is not None:
            self.query["range"][name]["lt"] = lt
        if gte is not None:
            self.query["range"][name]["gte"] = gte
        if lte is not None:
            self.query["range"][name]["lte"] = lte


class Filter:
    ''' http://www.elastic.co/guide/en/elasticsearch/reference/1.5/query-dsl-filters.html '''
    def __init__(self, query):
        ''' Filter based on the Query object passed in the constructor '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.filter = {"filter": query.query}

    def extend(self, filter_name, arr):
        if not isinstance(arr, list):
            arr = [arr]
        Query.is_array_query(arr)
        filter_arr = Query.query_to_str_array(arr)
        if filter_name in self.filter["filter"]:
            if not isinstance(self.filter["filter"][filter_name], list):
                self.filter["filter"][filter_name] = [self.filter["filter"][filter_name]]
            self.filter["filter"][filter_name].extend(filter_arr)
        else:
            self.filter["filter"][filter_name] = filter_arr
        return self


class TermsFilter(Filter):

    @classmethod
    def get_terms_filter(cls, name, arr):
        return cls(Query.terms(name, arr, minimum_should_match=0))


class OrFilter(Filter):
    def __init__(self, querys):
        ''' Or Filter based on the Query object(s) passed in the constructor '''
        if isinstance(querys, Query):
            querys = [querys]
        Query.is_array_query(querys)
        arr = Query.query_to_str_array(querys)
        self.filter = {"filter": {"or": arr}}

    def extend(self, arr):
        return Filter.extend(self, "or", arr)


class AndFilter(Filter):
    def __init__(self, querys):
        ''' And Filter based on the Query object(s) passed in the constructor '''
        if isinstance(querys, Query):
            querys = [querys]
        Query.is_array_query(querys)
        arr = Query.query_to_str_array(querys)
        self.filter = {"filter": {"and": arr}}

    def extend(self, arr):
        return Filter.extend(self, "and", arr)


class NotFilter(Filter):
    def __init__(self, query):
        ''' And Filter based on the Query object(s) passed in the constructor '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.filter = {"filter": {"not": query.query}}


class Highlight():
    def __init__(self, fields, pre_tags=None, post_tags=None):
        ''' Highlight one or more fields in the search results. '''
        if not isinstance(fields, list):
            fields = [fields]
        self.highlight = {"highlight": {"fields": {}}}
        for field in fields:
            self.highlight["highlight"]["fields"][field] = {}

        if pre_tags is not None:
            if not isinstance(pre_tags, list):
                pre_tags = [pre_tags]
            self.highlight["highlight"].update({"pre_tags": pre_tags})
        if post_tags is not None:
            if not isinstance(post_tags, list):
                post_tags = [post_tags]
            self.highlight["highlight"].update({"post_tags": post_tags})


class QueryError(Exception):
    ''' Query error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
