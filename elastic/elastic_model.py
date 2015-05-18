'''
Used to build Elastic queries and filters to run searches.

An L{ElasticQuery} is used to build a L{Search} object.
L{Search.get_json_response()} runs the search request and returns
the elastic JSON results. Alternatively L{Search.get_result()}
can be used to return a processed form of the results without
leading underscores (I{e.g.} _type) which django template does not like.

An L{ElasticQuery} object can be built from L{Query} and L{Filter}
objects. There are factory methods within L{ElasticQuery} and L{Query}
classes that provide shortcuts to building common types of queries/filters.
When creating a new query the first port of call would therefore be
the factory methods in L{ElasticQuery}. If this does not provide the
exact components needed for the query then look into building it
from the L{Query} and L{Filter} parent and child classes.
'''
import json
import requests
import logging
from elastic.elastic_settings import ElasticSettings

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Search:
    ''' Used to run Elastic queries and return search hits, hit count or the mapping. '''

    def __init__(self, search_query=None, aggs=None, search_from=0, size=20, idx=ElasticSettings.idx('DEFAULT')):
        ''' Set up parameters to use in the search. L{ElasticQuery} is used to
        define a search query.
        @type  search_query: L{ElasticQuery}
        @keyword search_query: The elastic query to search (default: None).
        @type  search_from: integer
        @keyword search_from: Offset used in paginations (default: 0).
        @type  size: integer
        @keyword size: maximum number of hits to return (default: 20).
        @type  idx: string
        @keyword idx: index to search (default: default index defined in settings).
        '''
        self.url = (ElasticSettings.url() + '/' + idx + '/_search?size=' + str(size) +
                    '&from='+str(search_from))
        if search_query is not None:
            if not isinstance(search_query, ElasticQuery):
                raise QueryError("not an ElasticQuery")
            self.query = search_query.query

        if aggs is not None:
            if hasattr(self, 'query'):
                self.query.update(aggs.aggs)
            else:
                self.query = aggs.aggs

        self.size = size
        self.idx = idx

    @classmethod
    def index_exists(cls, idx, url=ElasticSettings.url()):
        ''' Check if an index exists. '''
        url += '/' + idx + '/_mapping'
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

    def get_result(self, add_idx_types=False):
        ''' Return the elastic context result. Note: django template does not
        like underscores in the context indexes (e.g. _type). '''
        json_response = self.get_json_response()
        context = {"query": self.query}
        content = []
        for hit in json_response['hits']['hits']:
            hit['_source']['idx_type'] = hit['_type']
            hit['_source']['idx_id'] = hit['_id']
            if 'highlight' in hit:
                hit['_source']['highlight'] = hit['highlight']
            content.append(hit['_source'])

        context["data"] = content
        context["total"] = json_response['hits']['total']
        context["size"] = self.size
        if add_idx_types:
            self._add_idx_types(context)
        return context

    def _add_idx_types(self, context):
        ''' Adding index types to the context.  '''
        idx_types = {}
        idxs = self.idx.split(",")
        for this_idx in idxs:
            if this_idx == ElasticSettings.idx('MARKER'):
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
        context["idxs"] = idx_types
        context["db"] = self.idx


class ElasticQuery():
    ''' Takes a Query to be used to construct Elastic query which can be
    used in L{Search<elastic_model.Search>}.

    I{Advanced options:}
    Sources can be defined to set the fields that operations return (see
    U{source filtering<www.elastic.co/guide/en/elasticsearch/reference/1.x/search-request-source-filtering.html>}).
    Also
    U{highlighting<www.elastic.co/guide/en/elasticsearch/reference/1.x/search-request-highlighting.html>}
    can be defined for one or more fields in search results.  '''

    def __init__(self, query, sources=None, highlight=None):
        ''' Query the elastic server for given elastic query.

        @type  query: Query
        @param query: The query to build the ElasticQuery from.
        @type  sources: array of result fields
        @keyword sources: The _source filtering to be used (default: None).
        @type  highlight: Highlight
        @keyword highlight: Define the highlighting of results (default: None).
        '''
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
        ''' Factory method for creating elastic Bool Query.

        @type  query_bool: L{BoolQuery}
        @param query_bool: The bool query to build the ElasticQuery from.
        @type  sources: array of result fields
        @keyword sources: The _source filtering to be used (default: None).
        @type  highlight: L{Highlight}
        @keyword highlight: Define the highlighting of results (default: None).
        @return L{ElasticQuery}
        '''
        if not isinstance(query_bool, BoolQuery):
            raise QueryError("not a BoolQuery")
        return cls(query_bool, sources, highlight)

    @classmethod
    def filtered_bool(cls, query_match, query_bool, sources=None, highlight=None):
        ''' Factory method for creating an elastic
        U{Filtered Query<www.elastic.co/guide/en/elasticsearch/reference/1.x/query-dsl-filtered-query.html>}
        (L{FilteredQuery<elastic_model.FilteredQuery>}) using a Bool filter.

        @type  query_bool: Query
        @param query_bool: The query to be used.
        @type  query_bool: BoolQuery
        @param query_bool: The bool query to used in the filter.
        @type  sources: array of result fields
        @keyword sources: The _source filtering to be used (default: None).
        @type  highlight: Highlight
        @keyword highlight: Define the highlighting of results (default: None).
        @return: L{ElasticQuery}
        '''
        if not isinstance(query_bool, BoolQuery):
            raise QueryError("not a BoolQuery")
        return ElasticQuery.filtered(query_match, Filter(query_bool), sources, highlight)

    @classmethod
    def filtered(cls, query_match, query_filter, sources=None, highlight=None):
        ''' Factory method for creating an elastic
        U{Filtered Query<www.elastic.co/guide/en/elasticsearch/reference/1.x/query-dsl-filtered-query.html>}
        (L{FilteredQuery<elastic_model.FilteredQuery>}).

        @type  query_bool: Query
        @param query_bool: The query to be used.
        @type  query_filter: Filter
        @param query_filter: The filter to be used.
        @type  sources: array of result fields
        @keyword sources: The _source filtering to be used (default: None).
        @type  highlight: Highlight
        @keyword highlight: Define the highlighting of results (default: None).
        @return: L{ElasticQuery}
        '''

        query = FilteredQuery(query_match, query_filter)
        return cls(query, sources, highlight)

    @classmethod
    def query_string(cls, query_term, sources=None, highlight=None, **string_opts):
        ''' Factory method for creating elastic Query String Query.

        @type  query_term: string
        @param query_term: The string to use in the query.
        @type  sources: array of result fields
        @keyword sources: The _source filtering to be used (default: None).
        @type  highlight: Highlight
        @keyword highlight: Define the highlighting of results (default: None).
        @return: L{ElasticQuery}
        '''
        query = Query.query_string(query_term, **string_opts)
        return cls(query, sources, highlight)

    @classmethod
    def query_match(cls, match_id, match_str, sources=None, highlight=None):
        ''' Factory method for creating elastic Match Query.

        @type  match_id: string
        @param match_id: The match id.
        @type  match_str: string
        @param match_str: The string value to match.
        @type  sources: array of result fields
        @keyword sources: The _source filtering to be used (default: None).
        @type  highlight: Highlight
        @keyword highlight: Define the highlighting of results (default: None).
        @return: L{ElasticQuery}
        '''
        query = Query.match(match_id, match_str)
        return cls(query, sources, highlight)


class Query:
    ''' Used to build various queries, see
    U{Elastic query docs<www.elastic.co/guide/en/elasticsearch/reference/1.x/query-dsl-queries.html>}. '''

    def __init__(self, query):
        '''
        @type  query: dictionary
        @param query: The query in JSON format.
        '''
        if not isinstance(query, dict):
            raise QueryError("query is not a dictionary")
        self.query = query

    ''' String Query options '''
    STRING_OPTS = ["fields", "default_field", "default_operator",
                   "analyzer", "allow_leading_wildcard", "lowercase_expanded_terms",
                   "enable_position_increments", "fuzzy_max_expansions", "fuzzy_prefix_length",
                   "phrase_slop", "boost", "analyze_wildcard", "auto_generate_phrase_queries",
                   "max_determinized_states", "minimum_should_match", "lenient", "time_zone"]

    def query_wrap(self):
        ''' Wrap the query in a query parent. This is needed for some queries within
        a filter (I{e.g.} Query Match, Query String).
        @return: L{Query}
        '''
        query_wrap = {}
        query_wrap["query"] = self.query
        self.query = query_wrap
        return self

    @classmethod
    def match_all(cls):
        ''' Factory method for Match All Query
        @return: L{QUery}
        '''
        return cls({"match_all": {}})

    @classmethod
    def ids(cls, ids, types=None):
        ''' Factory method for Ids Query.
        @type  ids: array
        @param ids: The Ids values.
        @type  types: string or array
        @keyword types: Optionally provide a type of array of types (default: None).
        @return: L{Query}
        '''
        if not isinstance(ids, list):
            ids = [ids]
        if types is None:
            return cls({"ids": {"values": ids}})
        else:
            return cls({"ids": {"values": ids, "type": types}})

    @classmethod
    def term(cls, name, value, boost=None):
        ''' Factory method for Term Query.
        @type  name: name
        @param name: The name of the term.
        @type  value: value
        @param value: The value of the term.
        @type  boost: float
        @keyword boost: boost term query (default: None).
        @return: L{Query}
        '''
        if boost is None:
            return cls({"term": {name: value}})
        return cls({"term": {name: {"value": value, "boost": boost}}})

    @classmethod
    def terms(cls, name, arr, minimum_should_match=1):
        ''' Factory method for Terms Query.
        @type  name: name
        @param name: The name of the field.
        @type  arr: array
        @param arr: The terms to match.
        @type  minimum_should_match: integer, percentage
        @keyword minimum_should_match:
        U{minimum_should_match<www.elastic.co/guide/en/elasticsearch/reference/1.x/query-dsl-minimum-should-match.html>}
        @return: L{Query}
        '''
        if minimum_should_match != 0:
            query = {"terms": {name: arr, "minimum_should_match": minimum_should_match}}
        else:
            query = {"terms": {name: arr}}
        return cls(query)

    @classmethod
    def match(cls, match_id, match_str):
        ''' Factory method for Basic match query.
        @type  match_id: string
        @param match_id: The match id.
        @type  match_str: string
        @param match_str: The string value to match.
        @return: L{Query}
        '''
        return cls({"match": {match_id: match_str}})

    @classmethod
    def query_string(cls, query_term, **kwargs):
        ''' Factory method for
        U{Query String Query<www.elastic.co/guide/en/elasticsearch/reference/1.x/query-dsl-query-string-query.html>}.
        Simple wildcards can be used with the fields supplied
        (e.g. "fields" : ["city.*"]).

        @type  query_term: string
        @param query_term: The query string.
        @type  kwargs: L{STRING_OPTS}
        @keyword kwargs: Optional parameters for Query String Query.
        @return: L{Query}
        '''
        query = {"query_string": {"query": query_term}}

        for key, value in kwargs.items():
            if key not in Query.STRING_OPTS:
                raise QueryError("option "+key+" unrecognised as a String Query option")
            query["query_string"][key] = value
        return cls(query)

    @classmethod
    def _is_array_query(cls, arr):
        ''' Evaluate if array contents are Query objects. '''
        if not all(isinstance(y, (Query)) for y in arr):
            raise QueryError("not a Query")
        return True

    @classmethod
    def _query_to_str_array(cls, arr):
        ''' Return a str array from a query array. '''
        str_arr = []
        [str_arr.append(q.query) for q in arr]
        return str_arr


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

        Query._is_array_query(qarr)
        arr = Query._query_to_str_array(qarr)
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
    ''' Used to build various filters, see
    U{Elastic filter docs<www.elastic.co/guide/en/elasticsearch/reference/1.x/query-dsl-filters.html>} '''
    def __init__(self, query):
        ''' Filter based on a Query object.
        @type  query: L{Query}
        @param query: The query to build the filter with.
        '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.filter = {"filter": query.query}

    def extend(self, filter_name, arr):
        ''' Used to extend the named filter (I{e.g.} L{AndFilter}, L{OrFilter}).

        @type  filter_name: string
        @param filter_name: Name of the filter to extend.
        @type  arr: list of Query or Query
        @param arr: The Query(s) to add to the filter.
        @return: L{Filter}
        '''
        if not isinstance(arr, list):
            arr = [arr]
        Query._is_array_query(arr)
        filter_arr = Query._query_to_str_array(arr)
        if filter_name in self.filter["filter"]:
            if not isinstance(self.filter["filter"][filter_name], list):
                self.filter["filter"][filter_name] = [self.filter["filter"][filter_name]]
            self.filter["filter"][filter_name].extend(filter_arr)
        else:
            self.filter["filter"][filter_name] = filter_arr
        return self


class TermsFilter(Filter):
    ''' Terms Filter. '''

    @classmethod
    def get_terms_filter(cls, name, arr):
        return cls(Query.terms(name, arr, minimum_should_match=0))


class OrFilter(Filter):
    ''' Or Filter. '''
    def __init__(self, querys):
        ''' Or Filter based on the Query object(s) passed in the constructor '''
        if isinstance(querys, Query):
            querys = [querys]
        Query._is_array_query(querys)
        arr = Query._query_to_str_array(querys)
        self.filter = {"filter": {"or": arr}}

    def extend(self, arr):
        return Filter.extend(self, "or", arr)


class AndFilter(Filter):
    ''' And Filter. '''
    def __init__(self, querys):
        ''' And Filter based on the Query object(s) passed in the constructor '''
        if isinstance(querys, Query):
            querys = [querys]
        Query._is_array_query(querys)
        arr = Query._query_to_str_array(querys)
        self.filter = {"filter": {"and": arr}}

    def extend(self, arr):
        return Filter.extend(self, "and", arr)


class NotFilter(Filter):
    ''' Not Filter. '''
    def __init__(self, query):
        ''' And Filter based on the Query object(s) passed in the constructor '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.filter = {"filter": {"not": query.query}}


class Highlight():
    ''' Used in highlighting search result fields, see
    U{Elastic highlighting docs<www.elastic.co/guide/en/elasticsearch/reference/1.x/search-request-highlighting.html>}.
    '''
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


class Aggs():

    def __init__(self, agg_arr=None):
        self.aggs = {"aggregations": {}}
        if agg_arr is not None:
            if not isinstance(agg_arr, list):
                agg_arr = [agg_arr]
            for agg in agg_arr:
                self.aggs["aggregations"].update(agg.agg)


class Agg():

    AGGS = {"avg": {"type": dict, "params": {"field": str}},

            # bucket aggregation
            "global": {"type": dict},
            "filter": {"type": Query},
            "filters": {"type": list, "list_type": Query},
            "missing": {"type": dict, "params": {"field": str}},
            "terms": {"type": dict, "params": {"field": str, "size": int}},
            "significant_terms": {"type": dict, "params": {"field": str}},
            "range": {"type": dict, "params": {"field": str, 'ranges': list, "list_type": RangeQuery}}
            }

    def __init__(self, agg_name, agg_type, agg_body):
        self.agg = {agg_name: {}}
        AGGS = Agg.AGGS

        if agg_type in AGGS:
            if isinstance(agg_body, AGGS[agg_type]["type"]):
                if 'params' in Agg.AGGS[agg_type]:
                    for pkey in agg_body:
                        if pkey not in Agg.AGGS[agg_type]['params']:
                            raise QueryError('unrecognised aggregation parameter')
                        if not isinstance(agg_body[pkey], Agg.AGGS[agg_type]['params'][pkey]):
                            raise QueryError('aggregation parameter incorrect type')

                if 'list_type' in AGGS[agg_type]:
                    Agg._array_types(agg_body, AGGS[agg_type]['list_type'])
                    str_arr = []
                    [str_arr.append(Agg._get_query(q)) for q in agg_body]
                    self.agg[agg_name][agg_type] = str_arr
                else:
                    self.agg[agg_name][agg_type] = Agg._get_query(agg_body)
        print(json.dumps(self.agg))

    @classmethod
    def _get_query(cls, q):
        if hasattr(q, 'query'):
            return q.query
        return q

    @classmethod
    def _array_types(cls, arr, atype):
        ''' Evaluate if array contents are atype objects. '''
        if not all(isinstance(y, (atype)) for y in arr):
            raise QueryError("not a "+str(atype))
        return True


class QueryError(Exception):
    ''' Query error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
