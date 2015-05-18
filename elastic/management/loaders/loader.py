''' Parent loaders to handle mapping and bulk loading. '''
import gzip
import json
import requests
import re
from elastic.elastic_model import Search, ElasticSettings
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Loader:
    ''' Base loader class. Defines methods for loading the mapping for an
    index and bulk loading data. '''

    KEYWORD_ANALYZER = \
        {"analysis":
         {"analyzer":
          {"full_name":
           {"filter": ["standard", "lowercase"],
            "tokenizer": "keyword"}
           }
          }
         }

    def mapping(self, mapping, idx_type, meta=None, analyzer=None, **options):
        ''' Put the mapping (L{MappingProperties}) to the Elastic server. '''
        if not isinstance(mapping, MappingProperties):
            raise LoaderError("not a MappingProperties")

        idx_name = self.get_index_name(**options)
        url = ElasticSettings.url() + '/' + idx_name
        resp = requests.get(url)
        if resp.status_code == 200:
            logger.warn('WARNING: '+idx_name + ' index already exists!')
        else:
            # create index
            if analyzer is not None:
                resp = requests.put(url, json.dumps({'settings': analyzer}))
            else:
                requests.put(url)

        mapping_json = mapping.mapping_properties
        if meta is not None:
            mapping_json[idx_type]["_meta"] = meta

        # add mapping to index
        url += '/_mapping/' + idx_type
        resp = requests.put(url, data=json.dumps(mapping_json))
        self.mapping_json = mapping_json

        if(resp.status_code != 200):
            logger.warn('WARNING: '+idx_name+' mapping status: '+str(resp.status_code)+' '+str(resp.content))

    def bulk_load(self, idx_name, idx_type, json_data):
        ''' Bulk load documents. '''
#         nb = sys.getsizeof(json_data)
#         print(str(nb))
        resp = requests.put(ElasticSettings.url()+'/' + idx_name+'/' + idx_type +
                            '/_bulk', data=json_data)
        if(resp.status_code != 200):
            logger.error('ERROR: '+idx_name+' load status: '+str(resp.status_code)+' '+str(resp.content))

        # report errors found during loading
        if 'errors' in resp.json() and resp.json()['errors']:
            logger.error("ERROR: bulk load error found")
            for item in resp.json()['items']:
                for key in item.keys():
                    if 'error' in item[key]:
                        logger.error("ERROR LOADING:")
                        logger.error(item)

    def get_index_name(self, **options):
        ''' Get indexName option. '''
        if options['indexName']:
            return options['indexName'].lower()
        return self.__class__.__name__

    def open_file_to_load(self, file_name, **options):
        ''' Open the given file. '''
        if options[file_name].endswith('.gz'):
            return gzip.open(options[file_name], 'rb')
        else:
            return open(options[file_name], 'rb')

    def is_str(self, column_name, idx_name, idx_type):
        ''' Looks at the mapping to determine if the type is a string. '''
        if not self.mapping_json:
            self.mapping_json = Search(idx=idx_name).get_mapping(idx_type)[idx_name]['mappings']
        try:
            map_type = self.mapping_json[idx_type]["properties"][column_name]["type"]
        except KeyError:
            return False
        if map_type == 'string':
            return True
        return False

    def get_index_type(self, default_type, **options):
        if options['indexType']:
            return options['indexType'].lower()
        return default_type


class MappingProperties():
    ''' Used to create the mapping properties for an index. '''

    def __init__(self, idx_type):
        ''' For a given index type create the mapping properties. '''
        self.idx_type = idx_type
        self.mapping_properties = {self.idx_type: {"properties": {}}}
        self.column_names = []

    def add_property(self, name, map_type, index=None, analyzer=None, property_format=None):
        ''' Add a property to the mapping. '''
        self.mapping_properties[self.idx_type]["properties"][name] = {"type": map_type}
        if index is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"index": index})
        if analyzer is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"analyzer": analyzer})
        if property_format is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"format": property_format})
        self.column_names.append(name)
        return self

    def add_properties(self, mapping_properties):
        ''' Add a nested set of properties to the mapping. '''
        if not isinstance(mapping_properties, MappingProperties):
            raise LoaderError("not a MappingProperties")
        self.mapping_properties[self.idx_type]["properties"].update(mapping_properties.mapping_properties)
        return self

    def get_column_names(self):
        return self.column_names


class DelimeterLoader(Loader):
    ''' Loader for files with delimited columns (comma, tab I{etc}). '''

    def load(self, column_names, file_handle, idx_name, idx_type='tab', delim='\t',
             is_GFF=False, is_GTF=False, chunk=5000):
        ''' Index tab data '''
        json_data = ''
        line_num = 0
        auto_num = 1

        try:
            for line in file_handle:
                line = line.decode("utf-8")
                if(line.startswith("#")):
                    continue
                parts = re.split(delim, line)
                if len(parts) != len(column_names):
                    logger.warn("WARNING: unexpected number of columns: ["+str(line_num+1)+'] '+line)
                    continue

                idx_id = str(auto_num)
                json_data += '{"index": {"_id": "%s"}}\n' % idx_id

                doc_data = self.parse_line(parts, column_names, idx_name, idx_type, is_GFF, is_GTF)
                json_data += json.dumps(doc_data) + '\n'

                line_num += 1
                auto_num += 1
                if(line_num > chunk):
                    line_num = 0
                    print('.', end="", flush=True)
                    self.bulk_load(idx_name, idx_type, json_data)
                    json_data = ''
        finally:
            self.bulk_load(idx_name, idx_type, json_data)
            logger.info('No. documents loaded: '+str(auto_num-1))

    def parse_line(self, parts, column_names, idx_name, idx_type, is_GFF, is_GTF):
        ''' Parse the parts that make up the line. '''
        doc_data = {}
        for idx, p in enumerate(parts):
            p = p.strip()

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
        return doc_data

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
    ''' Loader for JSON data. '''

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


class LoaderError(Exception):
    ''' Loader error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
