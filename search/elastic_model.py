import json
import requests
import logging
from search.elastic_settings import ElasticSettings
from builtins import classmethod

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Elastic:
    ''' Used to run Elastic searches and return results or mappings. '''

    def __init__(self, build_query=None, search_from=0, size=20, db=ElasticSettings.idx('DEFAULT')):
        ''' Query the elastic server for given search query '''
        self.url = (ElasticSettings.url() + '/' + db + '/_search?size=' + str(size) +
                    '&from='+str(search_from))
        if build_query is not None:
            if not isinstance(build_query, ElasticQuery):
                raise QueryError("not an ElasticQuery")
            self.query = build_query.query
        self.size = size
        self.db = db

    @classmethod
    def range_overlap_query(cls, seqid, start_range, end_range,
                            search_from=0, size=20, db=ElasticSettings.idx('DEFAULT'),
                            field_list=None):
        ''' Constructs a range overlap query '''
        query_bool = BoolQuery(must_arr=[RangeQuery("start", lte=start_range),
                                         RangeQuery("end", gte=end_range)])
        or_filter = OrFilter(RangeQuery("start", gte=start_range, lte=end_range))
        or_filter.extend(RangeQuery("end", gte=start_range, lte=end_range))
        or_filter.extend(query_bool)
        query = ElasticQuery.filtered(Query.term("seqid", seqid), or_filter, field_list)
        return cls(query, search_from, size, db)

    @classmethod
    def field_search_query(cls, query_term, fields=None,
                           search_from=0, size=20, db=ElasticSettings.idx('DEFAULT')):
        ''' Constructs a field search query '''
        query = ElasticQuery.query_string(query_term, fields)
        return cls(query, search_from, size, db)

    def get_mapping(self, mapping_type=None):
        ''' Return the mappings for an index. '''
        self.mapping_url = (ElasticSettings.url() + '/' + self.db + '/_mapping')
        if mapping_type is not None:
            self.mapping_url += '/'+mapping_type
        response = requests.get(self.mapping_url)
        if response.status_code != 200:
            return json.dumps({"error": response.status_code})
        return response.json()

    def get_count(self):
        ''' Return the elastic count for a query result '''
        url = ElasticSettings.url() + '/' + self.db + '/_count?'
        response = requests.post(url, data=json.dumps(self.query))
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
        dbs = self.db.split(",")
        for this_db in dbs:
            stype = "Gene"
            if "snp" in this_db:
                stype = "Marker"
            if "region" in this_db:
                stype = "Region"
            c_dbs[this_db] = stype
        context["dbs"] = c_dbs
        context["db"] = self.db

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


class ElasticQuery:
    ''' Utility to assist in constructing Elastic queries. '''

    def __init__(self, query, sources=None):
        ''' Query the elastic server for given search query. '''
        if not isinstance(query, Query):
            raise QueryError("not a Query")
        self.query = {"query": query.query}
        if sources is not None:
            self.query["_source"] = sources

    @classmethod
    def bool(cls, query_bool):
        ''' Factory method for creating elastic Bool Query. '''
        if not isinstance(query_bool, BoolQuery):
            raise QueryError("not a BoolQuery")
        return cls(query_bool)

    @classmethod
    def filtered_bool(cls, query_match, query_bool, sources=None):
        ''' Factory method for creating elastic filtered query with Bool filter. '''
        if not isinstance(query_bool, BoolQuery):
            raise QueryError("not a BoolQuery")
        return ElasticQuery.filtered(query_match, Filter(query_bool), sources)

    @classmethod
    def filtered(cls, query_match, query_filter, sources=None):
        ''' Factory method for creating elastic Filtered Query. '''
        query = FilteredQuery(query_match, query_filter)
        return cls(query, sources)

    @classmethod
    def query_string(cls, query_term, fields=None, sources=None):
        ''' Factory method for creating elastic Query String Query '''
        query = Query.string(query_term, fields)
        return cls(query, sources)

    @classmethod
    def query_match(cls, match_id, match_str, sources=None):
        ''' Factory method for creating elastic Match Query. '''
        query = Query.match(match_id, match_str)
        return cls(query, sources)


class Query:

    def __init__(self, query):
        ''' Match query '''
        self.query = query

    @classmethod
    def match_all(cls):
        ''' Match All Query '''
        return cls({"match_all": {}})

    @classmethod
    def term(cls, name, value):
        ''' Term Query '''
        return cls({"term": {name: value}})

    @classmethod
    def match(cls, match_id, match_str):
        ''' Basic match query '''
        return cls({"match": {match_id: match_str}})

    @classmethod
    def string(cls, query_term, fields=None):
        ''' String query using a query parser in order to parse its content.
        Simple wildcards can be used with the fields supplied
        (e.g. "fields" : ["city.*"].) '''
        query = {"query_string": {"query": query_term}}
        if fields is not None:
            query["query_string"]["fields"] = fields
        return cls(query)

    @classmethod
    def is_array_query(cls, arr):
        for e in arr:
            if not isinstance(e, Query):
                raise QueryError("not a Query")
        return True

    @classmethod
    def query_to_str_array(cls, arr):
        query_arr = []
        [query_arr.append(q.query) for q in arr]
        return query_arr


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
        self._update("must", must_arr)

    def must_not(self, must_not_arr):
        self._update("must_not", must_not_arr)

    def should(self, should_arr):
        self._update("should", should_arr)

    def _update(self, name, qarr):
        if not isinstance(qarr, list):
            qarr = [qarr]

        Query.is_array_query(qarr)
        arr = Query.query_to_str_array(qarr)
        if name in self.query["bool"]:
            self.query["bool"][name].extend(arr)
        else:
            self.query["bool"][name] = arr


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


class OrFilter(Filter):
    def __init__(self, querys):
        ''' Or Filter based on the Query object(s) passed in the constructor '''
        if isinstance(querys, Query):
            querys = [querys]
        Query.is_array_query(querys)
        arr = Query.query_to_str_array(querys)
        self.filter = {"filter": {"or": arr}}

    def extend(self, arr):
        Filter.extend(self, "or", arr)


class AndFilter(Filter):
    def __init__(self, querys):
        ''' And Filter based on the Query object(s) passed in the constructor '''
        if isinstance(querys, Query):
            querys = [querys]
        Query.is_array_query(querys)
        arr = Query.query_to_str_array(querys)
        self.filter = {"filter": {"and": arr}}

    def extend(self, arr):
        Filter.extend(self, "and", arr)


class QueryError(Exception):
    ''' Query error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
