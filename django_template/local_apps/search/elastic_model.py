import json
import requests
from django.conf import settings
import re


class Elastic:

    def __init__(self, query=None, search_from=0, size=20, db=settings.MARKERDB):
        ''' Query the elastic server for given search query '''
        self.url = (settings.ELASTICSEARCH_URL + '/' + db + '/_search?size=' + str(size) +
                    '&from='+str(search_from))
        self.query = query
        self.size = size
        self.db = db

    @classmethod
    def range_overlap_query(cls, seqid, start_range, end_range,
                            search_from=0, size=20, db=settings.MARKERDB,
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
    def field_search_query(cls, query_term, fields,
                           search_from=0, size=20, db=settings.MARKERDB):
        ''' Constructs a field search query '''
        query = {"query": {"query_string": {"query": query_term, "fields": fields}}}
        return cls(query, search_from, size, db)

    def get_result(self):
        ''' Return the elastic context result '''
        response = requests.post(self.url, data=json.dumps(self.query))
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
        if response.status_code != 200:
            context["error"] = ("Error: elastic response " +
                                json.dumps(response.json()))
            return context

        if(len(response.json()['hits']['hits']) >= 1):
            for hit in response.json()['hits']['hits']:
                self._addInfo(content, hit)
                hit['_source']['idx_type'] = hit['_type']
                hit['_source']['idx_id'] = hit['_id']
                content.append(hit['_source'])
                #print(hit['_source']) @IgnorePep8

        context["data"] = content
        context["total"] = response.json()['hits']['total']
        if(int(response.json()['hits']['total']) < self.size):
            context["size"] = response.json()['hits']['total']
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
