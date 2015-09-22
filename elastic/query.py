''' Define L{Query} and L{Filter} to be used in an L{ElasticQuery} '''
from elastic.exceptions import QueryError, FilterError


class Query:
    ''' Used to build various queries, see
    U{Elastic query docs<www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-queries.html>}. '''

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
        U{minimum_should_match<www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-minimum-should-match.html>}
        @return: L{Query}
        '''
        if minimum_should_match != 0:
            query = {"terms": {name: arr, "minimum_should_match": minimum_should_match}}
        else:
            query = {"terms": {name: arr}}
        return cls(query)

    @classmethod
    def missing_terms(cls, name, arr):
        ''' Factory method for Missing Terms Query.
         -d '{"query":{"filtered":{"filter":{"terms":{"group_name":["dil"]}}}}}'
         -d '{"query":{"filtered":{"filter":{"missing":{ "field":"group_name"}}}}}'
        @type  name: name
        @param name: The name of the field.
        @type  arr: array
        @param arr: The terms to match.
        @return: L{Query}
        '''
        query = {"missing": {name: arr}}
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
        U{Query String Query<www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html>}
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
    def query_type_for_filter(cls, ftype):
        ''' Used as a filter for an index type.
        @type  ftype: string
        @param ftype: Index type to filter.
        '''
        query = {"type": {"value": ftype}}
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
        ''' Construct a filtered query '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        if not isinstance(query_filter, Filter):
            raise QueryError("not a Filter")
        self.query = {"filtered": {"query": query.query}}
        self.query["filtered"].update(query_filter.filter)


class HasParentQuery(Query):
    ''' Has Parent Query. '''
    def __init__(self, parent_type, query):
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.query = {"has_parent": {"type": parent_type, "query": query.query}}


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
    U{Elastic filter docs<www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-filters.html>} '''
    def __init__(self, query):
        ''' Filter based on a Query object.
        @type  query: L{Query}
        @param query: The query to build the filter with.
        '''
        if not isinstance(query, Query):
            raise FilterError("not a Query")
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

    @classmethod
    def get_missing_terms_filter(cls, name, arr):
        return cls(Query.missing_terms(name, arr))


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
            raise FilterError("not a Query")
        self.filter = {"filter": {"not": query.query}}
