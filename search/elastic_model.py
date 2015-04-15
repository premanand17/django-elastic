import json
import requests
import re
import logging
from search.elastic_settings import ElasticSettings

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Elastic:
    ''' Elastic search '''

    def __init__(self, query=None, search_from=0, size=20, db=ElasticSettings.idx('DEFAULT')):
        ''' Query the elastic server for given search query '''
        self.url = (ElasticSettings.url() + '/' + db + '/_search?size=' + str(size) +
                    '&from='+str(search_from))
        self.query = query
        self.size = size
        self.db = db

    @classmethod
    def range_overlap_query(cls, seqid, start_range, end_range,
                            search_from=0, size=20, db=ElasticSettings.idx('DEFAULT'),
                            field_list=None):
        ''' Constructs a range overlap query '''
        query = {"filtered":
                 {"query":
                  {"term": {"seqid": seqid}},
                  "filter": {"or":
                             [{"range": {"start": {"gte": start_range, "lte": end_range}}},
                              {"range": {"end": {"gte": start_range, "lte": end_range}}},
                              {"bool":
                               {"must":
                                [{"range": {"start": {"lte": start_range}}},
                                 {"range": {"end": {"gte": end_range}}}
                                 ]
                                }
                               }
                              ]
                             }
                  }
                 }

        if field_list is not None:
            query = {"_source": field_list, "query": query}
        else:
            query = {"query": query}
        return cls(query, search_from, size, db)

    @classmethod
    def field_search_query(cls, query_term, fields=None,
                           search_from=0, size=20, db=ElasticSettings.idx('DEFAULT')):
        ''' Constructs a field search query '''
        query = {"query": {"query_string": {"query": query_term}}}
        if fields is not None:
            query["query"]["query_string"]["fields"] = fields

        return cls(query, search_from, size, db)

    def get_mapping(self, mapping_type=None):
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
                self._addInfo(content, hit)
                hit['_source']['idx_type'] = hit['_type']
                hit['_source']['idx_id'] = hit['_id']
                content.append(hit['_source'])
                # print(hit['_source'])

        context["data"] = content
        context["total"] = json_response['hits']['total']
        if(int(json_response['hits']['total']) < self.size):
            context["size"] = json_response['hits']['total']
        else:
            context["size"] = self.size
        return context

    def _addInfo(self, content, hit):
        ''' Parse VCF INFO field and add to the search hit '''
        if 'info' not in hit['_source']:
            return
        ''' Split and add INFO tags and values '''
        infos = re.split(';', hit['_source']['info'])
        for info in infos:
            if "=" in info:
                parts = re.split('=', info)
                if parts[0] not in hit['_source']:
                    hit['_source'][parts[0]] = parts[1]
            else:
                if info not in hit['_source']:
                    hit['_source'][info] = ""


class Query:

    def __init__(self, query, sources=None):
        ''' Query the elastic server for given search query '''
        self.query = {"query": query}
        if sources is not None:
            self.query["_source"] = sources

    @classmethod
    def filtered(cls, query_match, query_bool, sources=None):
        ''' '''
        if not isinstance(query_match, QueryMatch):
            raise QueryError("not a QueryMatch")

        query_filter = QueryFilter.bool(query_bool)
        query = {"filtered": {"query": query_match.qmatch}}
        query["filtered"].update(query_filter.filter)
        return cls(query, sources)


class QueryMatch:

    def __init__(self, qmatch):
        ''' Match query '''
        self.qmatch = qmatch

    @classmethod
    def match_all(cls):
        qmatch = {"match_all": {}}
        return cls(qmatch)


class QueryBool:

    def __init__(self):
        ''' Bool query '''
        self.bool = {"bool": {}}

    def must(self, must_arr):
        self._update("must", must_arr)

    def must_not(self, must_not_arr):
        self._update("must_not", must_not_arr)

    def should(self, should_arr):
        self._update("should", should_arr)

    def _update(self, name, arr):
        if not isinstance(arr, list):
            arr = [arr]
        if name in self.bool["bool"]:
            self.bool["bool"][name].extend(arr)
        else:
            self.bool["bool"][name] = arr


class QueryFilter:

    def __init__(self, qfilter):
        ''' Filter query '''
        self.filter = {"filter": qfilter}

    @classmethod
    def bool(cls, query_bool):
        if not isinstance(query_bool, QueryBool):
            raise QueryError("not a QueryBool")
        return cls(query_bool.bool)

#     @classmethod
#     def or(cls, query_or):
#         if not isinstance(query_or, QueryOr):
#             raise QueryError("not a QueryOr")
#         return cls(query_or.or)


class QueryError(Exception):
    ''' GFF parse error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
