from django.conf import settings
from django.core.management.base import BaseCommand
from optparse import make_option
import gzip, re
import json, requests
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Use to create an elasticsearch index and add data \n" \
      "python manage.py index_search --snp --build dbSNP142\n" \
      "python manage.py index_search --loadSNP --build dbSNP142 All.vcf.gz"
    
    option_list = BaseCommand.option_list + (
        make_option('--snp',
            dest='snp',
            action="store_true",
            help='Create SNP index mapping'),
        ) + (
        make_option('--loadSNP',
            dest='loadSNP',
            help='VCF file to index'),
        ) + (
        make_option('--build',
            dest='build',
            help='Build number'),
        )

    '''
    Create the mapping for snp indexing
    '''
    def _create_snp_index(self, **options):    
        if options['build']:
            build = options['build'].lower()
        else:
            build = "snp"
            
        data = {
                "mappings": {
                        build: {
                                "properties": {
                                            "ID": { "type": "string", "boost": 4 },
                                            "SRC": { "type": "string" },
                                            "REF": { "type": "string", "index" : "no" },
                                            "ALT": { "type": "string", "index" : "no" },
                                            "POS": { "type": "integer", "index" : "not_analyzed" },
                                            "INFO" : {"type": "string", "index" : "no" }
                                        }
                                }
                        }
                }
        response = requests.put(settings.ELASTICSEARCH_URL+'/'+build+'/', data=json.dumps(data))
        print (response.text)
        return

    '''
    Index snp data
    '''
    def _create_load_snp_index(self, **options):
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
#                     if(line.startswith("##INFO=<")):
#                         parts = re.split(',', line[8:-1])
#                         id = ""
#                         desc = ""
#                         for p in parts:
#                             if(p.startswith("ID=")):
#                                 id = p[3:]
#                             elif(p.startswith("Description=")):
#                                 desc = re.sub(r'^"|"$', '', p[12:])
#                         if(id):
#                             info[id] = desc
                    continue
                
                src = parts[0]
                data += '{"index": {"_id": "%s"}}\n' % nn
                data += json.dumps({
                        "ID": parts[2],
                        "SRC": src,
                        "REF": parts[3],
                        "ALT": parts[4],
                        "POS": int(parts[1])+1,
                        "INFO" : parts[7]
                        })+'\n'                                  

                n += 1
                nn += 1
                if( n > 5000 ):
                    n = 0
                    
                    if(lastSrc != src):
                        print ('\nLoading '+src)
                    print('.',end="",flush=True)
                    response = requests.put(settings.ELASTICSEARCH_URL+'/'+build+'/snp/_bulk', data=data)
                    #print (response.text)
                    data = ''
                    lastSrc = src

        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/'+build+'/snp/_bulk', data=data)

        return

    def handle(self, *args, **options):
        if options['snp']:
          self._create_snp_index(**options)
        elif options['loadSNP']:
          self._create_load_snp_index(**options)
        else:
          print(help)
