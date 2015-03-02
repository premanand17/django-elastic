import re
from django_template import settings
import requests
import json


class DiseaseManager:

    def create_disease(self, **options):
        ''' Disease loading '''
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "disease"

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
            resp = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                indexName+'/disease/'+parts[2],
                                data=data)

            if resp.status_code == 201:
                print ("Loaded "+parts[0])
            else:
                print ("Problem loading "+parts[0])

    def create_disease_index(self, **options):
        ''' Create the mapping for disease indexing '''
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "disease"

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
        requests.put(settings.ELASTICSEARCH_URL+'/' + indexName)
        response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                indexName+'/_mapping/disease',
                                data=json.dumps(data))
        print (response.text)
        return
