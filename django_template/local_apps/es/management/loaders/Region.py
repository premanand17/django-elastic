import json
from db.management.loaders.GFF import GFF
import re
import requests
from django.conf import settings


class RegionManager:

    ''' Index region data '''
    def create_load_region_index(self, **options):
        index_name = self.create_index_name(**options)
        print('GFF file to be loaded: ' + options['indexRegion'])
        if options['disease']:
            disease = options['disease'].lower()
        else:
            disease = "all"
        f = open(options['indexRegion'], 'r')
        json_data = ''
        line_num = 0
        auto_num = 0
        lastLine = ''

        try:
            for line in f:
                current_line = line.rstrip()
                if(current_line.startswith("#")):
                    continue
                parts = re.split('\t', current_line)
                if(len(parts) != 9):
                    continue
                gff = GFF(current_line)
                json_data += '{"index": {"_id": "%s"}}\n' % auto_num
                json_data += json.dumps({"seqid": gff.seqid,
                                         "source": gff.source,
                                         "type": gff.type,
                                         "start": gff.start,
                                         "end": gff.end,
                                         "score": gff.score,
                                         "strand": gff.strand,
                                         "phase": gff.phase,
                                         "attr": gff.attrs
                                         }) + '\n'
                line_num += 1
                auto_num += 1
                if(line_num > 5):
                    line_num = 0

                    if(lastLine != line):
                        print ('\nAutonum ' + str(auto_num) +
                               ' Loading from line:' + line)
                    print('.', end="", flush=True)
                    response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                            index_name+'/' + disease +
                                            '/_bulk', data=json_data
                                            )
                    json_data = ''
                    lastLine = line

        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                    index_name+'/' + disease +
                                    '/_bulk', data=json_data
                                    )
        return response

    '''
    Create the mapping for region indexing
    '''
    def create_region_index(self, **options):
        index_name = self.create_index_name(**options)
        if options['disease']:
            disease = options['disease'].lower()
        else:
            disease = "all"
        print('START Mapping for index ' + index_name + ' and type ' + disease)
        props = {"properties": {"seqid": {"type": "string",
                                "index": "no"},
                                "source": {"type": "string",
                                           "index": "no"},
                                "type": {"type": "string",
                                         "index": "not_analyzed"},
                                "start": {"type": "integer", "index":
                                          "not_analyzed"},
                                "end": {"type": "integer",
                                        "index": "not_analyzed"},
                                "score": {"type": "string",
                                          "index": "no"},
                                "strand": {"type": "string",
                                           "index": "no"},
                                "phase": {"type": "string",
                                          "index": "no"},
                                "attr": {"properties":
                                         {"tag": {"type": "string",
                                                  "index": "not_analyzed"},
                                          "value": {"type": "string"}
                                          }
                                         }
                                }
                 }

        # check if index exists
        response = requests.get(settings.ELASTICSEARCH_URL + '/' + index_name)
        print('Response status code ' + str(response.status_code))
        if(response.status_code != 200):
            requests.put(settings.ELASTICSEARCH_URL + '/' + index_name)
        data = {disease: props}
        response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                index_name+'/_mapping/' + disease,
                                data=json.dumps(data))
        print (response.text)
        return

    '''
    Create the index name combining build, disease code
    '''
    def create_index_name(self, **options):
        if options['build']:
            org_build = options['build'].lower()
        else:
            org_build = "nobuild"
        if options['indexName']:
            index_name = options['indexName'].lower()
        else:
            index_name = "disease_region" + "_" + org_build
        return index_name
