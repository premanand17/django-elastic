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
from elastic.result import Document, Result, Aggregation
from elastic.elastic_settings import ElasticSettings
from elastic.query import Query, QueryError, BoolQuery, RangeQuery, FilteredQuery,\
    Filter, OrFilter
import warnings

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
        return cls(search_query=query, search_from=search_from, size=size, idx=idx)

    @classmethod
    def field_search_query(cls, query_term, aggs=None, fields=None, search_from=0,
                           size=20, idx=ElasticSettings.idx('DEFAULT')):
        ''' Constructs a field elastic query '''
        query = ElasticQuery.query_string(query_term, fields=fields)
        return cls(search_query=query, aggs=aggs, search_from=search_from, size=size, idx=idx)

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
        ''' DEPRECATED: use Search.search().
        Return the elastic json result. Note: django template does not
        like underscores (e.g. _type). '''
        warnings.warn("Search.get_result will be removed, use Search.search()", FutureWarning)

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
        return context

    def search(self):
        ''' Run the search and return a L{Result} that stores the
        L{Document} and L{Aggregation} objects. '''
        json_response = self.get_json_response()
        hits = json_response['hits']['hits']
        docs = [Document(hit) for hit in hits]
        aggs = Aggregation.build_aggs(json_response)
        return Result(took=json_response['took'],
                      hits_total=json_response['hits']['total'],
                      size=self.size, docs=docs, aggs=aggs,
                      idx=self.idx, query=self.query)


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
