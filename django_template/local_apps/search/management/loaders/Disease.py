import re
from django.conf import settings
import requests
import json


class DiseaseManager:

    def create_disease(self, **options):
        ''' Disease loading '''
        index_name = self._get_index_name(**options)
        self.create_disease_mapping(**options)

        # read disease list as column tab delimited file
        f = open(options['indexDisease'], 'r')
        for line in f:
            if(line.startswith("#")):
                continue
            parts = re.split('\t', line)
            data = json.dumps({"name": parts[0],
                               "code": parts[2],
                               "description": parts[1],
                               "colour": parts[3],
                               "tier": int(parts[4])
                               })
            resp = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                index_name+'/disease/'+parts[2],
                                data=data)

            if resp.status_code == 201:
                print ("Loaded "+parts[0])
            else:
                print ("Problem loading "+parts[0])

    def create_disease_mapping(self, **options):
        ''' Create the mapping for disease indexing '''
        index_name = self._get_index_name(**options)

        props = {"properties":
                 {"name": {"type": "string", "boost": 4,
                           "index": "not_analyzed"},
                  "code": {"type": "string",
                           "index": "not_analyzed"},
                  "description": {"type": "string",
                                  "index": "not_analyzed"},
                  "colour": {"type": "string",
                             "index": "not_analyzed"},
                  "tier": {"type": "integer",
                           "index": "not_analyzed"},
                  }
                 }

        data = {"disease": props}
        ''' create index and add mapping '''
        requests.put(settings.SEARCH_ELASTIC_URL+'/' + index_name)
        requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                     index_name+'/_mapping/disease',
                     data=json.dumps(data))
        return

    def _get_index_name(self, **options):
        if options['indexName']:
            return options['indexName'].lower()
        return "disease"
