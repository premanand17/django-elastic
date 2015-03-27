import gzip
import json
import requests
from django.conf import settings


class Loader:

    KEYWORD_ANALYZER = \
        {"analysis":
         {"analyzer":
          {"full_name":
           {"filter": ["standard", "lowercase"],
            "tokenizer": "keyword"}
           }
          }
         }

    def mapping(self, mapping_json, analyzer=None, **options):
        ''' Put the mapping to the Elastic server '''
        index_name = self.get_index_name(**options)
        if analyzer is not None:
            mapping_json = self.append_analyzer(mapping_json, analyzer)
        requests.put(settings.SEARCH_ELASTIC_URL+'/' + index_name, data=json.dumps(mapping_json))
        return

    def append_analyzer(self, json, analyzer):
        ''' Append analyzer to mapping '''
        json['settings'] = analyzer
        return json

    def get_index_name(self, **options):
        ''' Get indexName option '''
        if options['indexName']:
            return options['indexName'].lower()
        return self.__class__.__name__

    def open_file_to_load(self, file_name, **options):
        ''' Open the given file '''
        if options[file_name].endswith('.gz'):
            return gzip.open(options[file_name], 'rb')
        else:
            return open(options[file_name], 'rb')
