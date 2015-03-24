import json
import requests
from django.conf import settings
import re


class Elastic:

    def __init__(self, data, search_from=0, size=20, db=settings.MARKERDB):
        ''' Query the elastic server for given search data '''
        self.url = (settings.ELASTICSEARCH_URL + '/' + db + '/_search?size=' + str(size) +
                    '&from='+str(search_from))
        self.data = data
        self.size = size
        self.db = db
        self.response = requests.post(self.url, data=json.dumps(data))

    def get_result(self):
        ''' Return the elastic context result '''
        context = {"query": self.data}
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
        if self.response.status_code != 200:
            context["error"] = ("Error: elastic response " +
                                json.dumps(self.response.json()))
            return context

        if(len(self.response.json()['hits']['hits']) >= 1):
            for hit in self.response.json()['hits']['hits']:
                self._addInfo(content, hit)
                hit['_source']['idx_type'] = hit['_type']
                hit['_source']['idx_id'] = hit['_id']
                content.append(hit['_source'])
                #print(hit['_source']) @IgnorePep8

        context["data"] = content
        context["total"] = self.response.json()['hits']['total']
        if(int(self.response.json()['hits']['total']) < self.size):
            context["size"] = self.response.json()['hits']['total']
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
