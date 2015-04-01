# import json
# from db.management.loaders.GFF import GFF
# import re
# import requests
# from django.conf import settings
# from django.core.management.base import CommandError
#
#


class RegionManager:

    def create_load_region_index(self, **options):
        return

    def create_region_index(self, **options):
        return

#
#     def create_load_region_index(self, **options):
#         ''' Index region data '''
#         print('GFF file to be loaded: ' + options['indexRegion'])
#         if options['disease']:
#             disease = options['disease'].lower()
#         else:
#             raise CommandError('Please provide the disease code')
#         if options['regionType']:
#             region_type = options['regionType'].lower()
#         else:
#             region_type = 'assoc'
#
#         index_name = self.create_index_name(**options)
#         index_type = 'region'
#
#         f = open(options['indexRegion'], 'r')
#         json_data = ''
#         line_num = 0
#         auto_num = 1
#         lastLine = ''
#
#         try:
#             for line in f:
#                 current_line = line.rstrip()
#                 if(current_line.startswith("#")):
#                     continue
#                 parts = re.split('\t', current_line)
#                 if(len(parts) != 9):
#                     continue
#                 gff = GFF(current_line)
#                 attrs = gff.attrs
#                 attrs['disease_code'] = disease
#                 attrs['region_type'] = region_type
#                 print(attrs)
#                 idx_id = disease + '_' + str(auto_num)
#                 json_data += '{"index": {"_id": "%s"}}\n' % idx_id
#                 json_data += json.dumps({"seqid": gff.seqid,
#                                          "source": gff.source,
#                                          "type": gff.type,
#                                          "start": gff.start,
#                                          "end": gff.end,
#                                          "score": gff.score,
#                                          "strand": gff.strand,
#                                          "phase": gff.phase,
#                                          "attr": attrs
#                                          }) + '\n'
#                 line_num += 1
#                 auto_num += 1
#                 if(line_num > 5):
#                     line_num = 0
#
#                     if(lastLine != line):
#                         print ('\nAutonum ' + str(auto_num) +
#                                ' Loading from line:' + line)
#                     print('.', end="", flush=True)
#                     response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
#                                             index_name+'/' + index_type +
#                                             '/_bulk', data=json_data
#                                             )
#                     json_data = ''
#                     lastLine = line
#
#         finally:
#             response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
#                                     index_name+'/' + index_type +
#                                     '/_bulk', data=json_data
#                                     )
#         return response
#
#     def create_region_index(self, **options):
#         ''' Create the mapping for region indexing '''
#         index_name = self.create_index_name(**options)
#         index_type = 'region'
#         print('Mapping for index ' + index_name + ' and type ' + index_type)
#         props = {"properties": {"seqid": {"type": "string"},
#                                 "source": {"type": "string"},
#                                 "type": {"type": "string",
#                                          "index": "not_analyzed"},
#                                 "start": {"type": "integer",
#                                           "index": "not_analyzed"},
#                                 "end": {"type": "integer",
#                                         "index": "not_analyzed"},
#                                 "score": {"type": "string",
#                                           "index": "no"},
#                                 "strand": {"type": "string",
#                                            "index": "no"},
#                                 "phase": {"type": "string",
#                                           "index": "no"},
#                                 "attr": {"type": "object"}
#                                 }
#                  }
#
#         # check if index exists
#         response = requests.get(settings.SEARCH_ELASTIC_URL + '/' + index_name)
#         if(response.status_code != 200):
#             print('Response status code ' + str(response.status_code) +
#                   'Creating new index ')
#         else:
#             print('Response status code ' + str(response.status_code) +
#                   ' Index already exists...Overriding the mapping')
#         requests.put(settings.SEARCH_ELASTIC_URL + '/' + index_name)
#         data = {index_type: props}
#         response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
#                                 index_name+'/_mapping/' + index_type,
#                                 data=json.dumps(data))
#         print (response.text)
#         return
#
#     def create_index_name(self, **options):
#         ''' Create the index name combining build, disease code '''
#         if options['build']:
#             org_build = options['build'].lower()
#         else:
#             org_build = "nobuild"
#         if options['indexName']:
#             index_name = options['indexName'].lower()
#         else:
#             index_name = "disease_region" + "_" + org_build
#         return index_name

