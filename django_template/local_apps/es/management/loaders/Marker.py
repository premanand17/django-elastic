import gzip
import re
import json
import requests
from django_template import settings


class MarkerManager:

    ''' Index snp data '''
    def create_load_snp_index(self, **options):
        if options['build']:
            build = options['build'].lower()
        else:
            build = "snp"

        if options['loadSNP'].endswith('.gz'):
            f = gzip.open(options['loadSNP'], 'rb')
        else:
            f = open(options['loadSNP'], 'rb')

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
                data += json.dumps({"ID": parts[2],
                                    "SRC": src,
                                    "REF": parts[3],
                                    "ALT": parts[4],
                                    "POS": int(parts[1])+1,
                                    "INFO": parts[7]
                                    })+'\n'

                n += 1
                nn += 1
                if(n > 5000):
                    n = 0

                    if(lastSrc != src):
                        print ('\nLoading '+src)
                    print('.', end="", flush=True)
                    response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                            build+'/snp/_bulk', data=data)
                    data = ''
                    lastSrc = src

        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                    build+'/snp/_bulk', data=data)
        return response

    '''
    Create the mapping for snp indexing
    '''
    def create_snp_index(self, **options):
        if options['build']:
            build = options['build'].lower()
        else:
            build = "snp"

        props = {"properties": {"ID": {"type": "string", "boost": 4},
                                "SRC": {"type": "string"},
                                "REF": {"type": "string",
                                        "index": "no"},
                                "ALT": {"type": "string",
                                        "index": "no"},
                                "POS": {"type": "integer",
                                        "index": "not_analyzed"},
                                "INFO": {"type": "string",
                                         "index": "no"}
                                }}

        data = {"mappings": {build: props}}
        response = requests.put(settings.ELASTICSEARCH_URL+'/'+build+'/',
                                data=json.dumps(data))
        print (response.text)
        return
