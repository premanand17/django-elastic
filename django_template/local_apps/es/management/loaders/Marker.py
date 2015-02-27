import gzip
import re
import json
import requests
from django_template import settings


class MarkerManager:

    ''' Index snp data '''
    def create_load_snp_index(self, **options):
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "snp"

        if options['indexSNP'].endswith('.gz'):
            f = gzip.open(options['indexSNP'], 'rb')
        else:
            f = open(options['indexSNP'], 'rb')

        data = ''
        n = 0
        nn = 0
        lastSrc = ''

        try:
            for line in f:
                line = line.rstrip().decode("utf-8")
                parts = re.split('\t', line)
                if(len(parts) != 8 or line.startswith("#")):
                    continue

                src = parts[0]
                data += '{"index": {"_id": "%s"}}\n' % nn
                data += json.dumps({"id": parts[2],
                                    "src": src,
                                    "ref": parts[3],
                                    "alt": parts[4],
                                    "pos": int(parts[1])+1,
                                    "info": parts[7]
                                    })+'\n'

                n += 1
                nn += 1
                if(n > 5000):
                    n = 0

                    if(lastSrc != src):
                        print ('\nLoading '+src)
                    print('.', end="", flush=True)
                    response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                            indexName+'/marker/_bulk',
                                            data=data)
                    data = ''
                    lastSrc = src

        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                    indexName+'/marker/_bulk', data=data)
        return response

    '''
    Create the mapping for snp indexing
    '''
    def create_snp_index(self, **options):
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "dbsnp"

        props = {"properties":
                 {"id": {"type": "string", "index": "not_analyzed",
                         "boost": 4},
                  "src": {"type": "string", "index": "not_analyzed"},
                  "ref": {"type": "string", "index": "no"},
                  "alt": {"type": "string", "index": "no"},
                  "pos": {"type": "integer", "index": "not_analyzed"},
                  "info": {"type": "string", "index": "no"}
                  }
                 }

        data = {"marker": props}

        ''' create index and add mapping '''
        requests.put(settings.ELASTICSEARCH_URL+'/' + indexName)
        response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                indexName+'/_mapping/marker',
                                data=json.dumps(data))
        print (response.text)
        return
