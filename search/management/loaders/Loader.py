import gzip
import json
import requests
from django.conf import settings
import re
from search.elastic_model import Elastic


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

    def mapping(self, mapping_json, idx_type, analyzer=None, **options):
        ''' Put the mapping to the Elastic server '''
        idx_name = self.get_index_name(**options)
        url = settings.SEARCH_ELASTIC_URL + '/' + idx_name
        resp = requests.get(url)
        if(resp.status_code == 200):
            print('WARNING: '+idx_name + ' index already exists!')
        else:
            # create index
            if analyzer is not None:
                resp = requests.put(url, json.dumps({'settings': analyzer}))
            else:
                requests.put(url)

        # add mapping to index
        url += '/_mapping/' + idx_type
        resp = requests.put(url, data=json.dumps(mapping_json))
        self.mapping_json = mapping_json

        if(resp.status_code != 200):
            print('WARNING: ' + idx_name + ' mapping status: ' + str(resp.status_code))
            print(resp.content)

    def bulk_load(self, idx_name, idx_type, json_data):
        ''' Bulk load documents '''
        resp = requests.put(settings.SEARCH_ELASTIC_URL+'/' + idx_name+'/' + idx_type +
                            '/_bulk', data=json_data)
        if(resp.status_code != 200):
            print('ERROR: ' + idx_name + ' load status: ' + str(resp.status_code))
            print(resp.content)

    def document_update(self, idx_name, idx_type, doc_id, update_json):
        ''' Update a document as described in the Elastic API
        http://www.elastic.co/guide/en/elasticsearch/reference/current/docs-update.html '''
        resp = requests.post(settings.SEARCH_ELASTIC_URL+'/' + idx_name+'/' +
                             idx_type + '/' + doc_id + '/_update', data=update_json)
        if(resp.status_code != 200):
            print('ERROR: ' + idx_name + 'document id: ' + doc_id +
                  ' update status: ' + str(resp.status_code))

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

    def is_str(self, column_name, idx_name, idx_type):
        ''' Looks at the mapping to determine if the type is a string '''
        if not self.mapping_json:
            elastic = Elastic(db=idx_name)
            self.mapping_json = elastic.get_mapping(idx_type)
        try:
            map_type = self.mapping_json["mappings"][idx_type]["properties"][column_name]["type"]
        except KeyError:
            return False
        if map_type == 'string':
            return True
        return False


class DelimeterLoader(Loader):

    def load(self, column_names, file_handle, idx_name, idx_type='tab', delim='\t',
             is_GFF=False, is_GTF=False):
        ''' Index tab data '''
        json_data = ''
        line_num = 0
        auto_num = 1

        try:
            for line in file_handle:
                line = line.rstrip().decode("utf-8")
                current_line = line
                if(current_line.startswith("#")):
                    continue
                parts = re.split(delim, current_line)
                if len(parts) != len(column_names):
                    print("WARNING: unexpected number of columns")
                    print(line)
                    continue

                idx_id = str(auto_num)
                json_data += '{"index": {"_id": "%s"}}\n' % idx_id

                doc_data = {}
                attrs = {}
                for idx, p in enumerate(parts):
                    if (is_GFF or is_GTF) and idx == len(parts)-1:
                        if is_GTF:
                            attrs = self._getAttributes(p, key_value_delim=' ')
                        else:
                            attrs = self._getAttributes(p)
                        doc_data[column_names[idx]] = attrs
                        continue

                    if self.is_str(column_names[idx], idx_name, idx_type):
                        doc_data[column_names[idx]] = p
                    elif p.isdigit():
                        doc_data[column_names[idx]] = int(p)
                    elif self._isfloat(p):
                        doc_data[column_names[idx]] = float(p)
                    else:
                        doc_data[column_names[idx]] = p

                json_data += json.dumps(doc_data) + '\n'

                line_num += 1
                auto_num += 1
                if(line_num > 5000):
                    line_num = 0
                    print('.', end="", flush=True)
                    self.bulk_load(idx_name, idx_type, json_data)
                    json_data = ''
        finally:
            self.bulk_load(idx_name, idx_type, json_data)
            print('No. documents loaded: '+str(auto_num))

    def _getAttributes(self, attrs, key_value_delim='='):
        ''' Parse the attributes column '''
        parts = re.split(';', attrs)
        attrs_arr = {}
        for p in parts:
            if(p == ''):
                continue
            at = re.split(key_value_delim, p.strip())
            if len(at) == 2:
                attrs_arr[at[0]] = at[1]
            else:
                attrs_arr[at[0]] = ""
        return attrs_arr

    def _isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False


class JSONLoader(Loader):

    def load(self, raw_json_data, idx_name, idx_type='json'):
        ''' Index raw json data '''
        json_data = ''
        line_num = 0
        auto_num = 1
        try:
            for row in raw_json_data:
                idx_id = str(auto_num)
                json_data += '{"index": {"_id": "%s"}}\n' % idx_id
                json_data += json.dumps(row) + '\n'
                auto_num += 1
                line_num += 1

                if(line_num > 5000):
                    line_num = 0
                    print('.', end="", flush=True)
                    self.bulk_load(idx_name, idx_type, json_data)
                    json_data = ''
        finally:
            self.bulk_load(idx_name, idx_type, json_data)
