import gzip
import re
import json
import requests
from django.conf import settings


class MarkerManager:

    def create_load_snp_index(self, **options):
        ''' Index snp data '''
        index_name = self._get_index_name(**options)
        self._create_snp_index(**options)

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
                if not src.startswith("chr"):
                    src = "chr"+src
                data += '{"index": {"_id": "%s"}}\n' % nn
                data += json.dumps({"id": parts[2],
                                    "seqid": src,
                                    "ref": parts[3],
                                    "alt": parts[4],
                                    "start": int(parts[1]),
                                    "end": int(parts[1]),
                                    "info": parts[7]
                                    })+'\n'

                n += 1
                nn += 1
                if(n > 5000):
                    n = 0

                    if(lastSrc != src):
                        print ('\nLoading '+src)
                    print('.', end="", flush=True)
                    response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                            index_name+'/marker/_bulk',
                                            data=data)
                    data = ''
                    lastSrc = src

        finally:
            response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                    index_name+'/marker/_bulk', data=data)
        return response

    def _create_snp_index(self, **options):
        ''' Create the mapping for snp indexing '''
        index_name = self._get_index_name(**options)

        props = {"properties":
                 {"id": {"type": "string", "index": "not_analyzed",
                         "boost": 4},
                  "seqid": {"type": "string", "index": "not_analyzed"},
                  "ref": {"type": "string", "index": "no"},
                  "alt": {"type": "string", "index": "no"},
                  "start": {"type": "integer", "index": "not_analyzed"},
                  "end": {"type": "integer", "index": "not_analyzed"},
                  "info": {"type": "string", "index": "no"}
                  }
                 }

        data = {"marker": props}

        ''' create index and add mapping '''
        requests.put(settings.SEARCH_ELASTIC_URL+'/' + index_name)
        requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                     index_name+'/_mapping/marker',
                     data=json.dumps(data))
        return

    def _get_index_name(self, **options):
        if options['indexName']:
            return options['indexName'].lower()
        return "dbsnp"
