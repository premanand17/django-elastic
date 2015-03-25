from db.management.loaders.GFF import GFF
from django.conf import settings
import re
import requests
import gzip
import json


class GFFManager:

    def create_load_gff_index(self, **options):
        ''' Index gff data '''
        self._create_gff_mapping(**options)
        index_name = self._get_index_name(**options)
        index_type = self._get_index_type(**options)
        if options['indexGFF'].endswith('.gz'):
            f = gzip.open(options['indexGFF'], 'rb')
        else:
            f = open(options['indexGFF'], 'rb')

        json_data = ''
        line_num = 0
        auto_num = 1

        try:
            for line in f:
                line = line.rstrip().decode("utf-8")
                current_line = line
                if(current_line.startswith("#")):
                    continue
                parts = re.split('\t', current_line)
                if(len(parts) != 9):
                    continue

                if options['isGTF']:
                    gff = GFF(current_line, key_value_delim=' ')
                else:
                    gff = GFF(current_line)
                attrs = gff.attrs
                idx_id = index_type + '_' + str(auto_num)
                json_data += '{"index": {"_id": "%s"}}\n' % idx_id
                json_data += json.dumps({"seqid": gff.seqid,
                                         "source": gff.source,
                                         "type": gff.type,
                                         "start": gff.start,
                                         "end": gff.end,
                                         "score": gff.score,
                                         "strand": gff.strand,
                                         "phase": gff.phase,
                                         "attr": attrs
                                         }) + '\n'
                line_num += 1
                auto_num += 1
                if(line_num > 5000):
                    line_num = 0
                    print('.', end="", flush=True)
                    response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                            index_name+'/' + index_type +
                                            '/_bulk', data=json_data
                                            )
                    json_data = ''
        finally:
            response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                    index_name+'/' + index_type +
                                    '/_bulk', data=json_data
                                    )
        return response

    def _create_gff_mapping(self, **options):
        ''' Create the mapping for region indexing '''
        index_name = self._get_index_name(**options)
        index_type = self._get_index_type(**options)
        print('Mapping for index ' + index_name + ' and type ' + index_type)
        props = {"properties": {"seqid": {"type": "string"},
                                "source": {"type": "string"},
                                "type": {"type": "string",
                                         "index": "not_analyzed"},
                                "start": {"type": "integer",
                                          "index": "not_analyzed"},
                                "end": {"type": "integer",
                                        "index": "not_analyzed"},
                                "score": {"type": "string",
                                          "index": "no"},
                                "strand": {"type": "string",
                                           "index": "no"},
                                "phase": {"type": "string",
                                          "index": "no"},
                                "attr": {"type": "object"}
                                }
                 }

        # check if index exists
        response = requests.get(settings.SEARCH_ELASTIC_URL + '/' + index_name)
        if(response.status_code != 200):
            print('Response status code ' + str(response.status_code) +
                  'Creating new index ')
        else:
            print('Response status code ' + str(response.status_code) +
                  ' Index already exists...Overriding the mapping')
        requests.put(settings.SEARCH_ELASTIC_URL + '/' + index_name)
        data = {index_type: props}
        response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                index_name+'/_mapping/' + index_type,
                                data=json.dumps(data))
        print (response.text)
        return

    def _get_index_name(self, **options):
        if options['indexName']:
            return options['indexName'].lower()
        return "gff"

    def _get_index_type(self, **options):
        if options['indexType']:
            return options['indexType'].lower()
        return "gff"
