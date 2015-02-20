import gzip
import re
import requests
from django_template import settings
import json


class GenenameManager:

    '''
    Create index based on genenames.org download file for names
    (http://www.genenames.org/cgi-bin/download).
    The file is assumed to include the following columns:
    hgnc id, approved symbol, status, locus type, previous symbols
    synonyms, entrez gene id, ensembl gene id
    '''
    def load_genename(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'

        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "gene"

        if options['indexGene'].endswith('.gz'):
            f = gzip.open(options['indexGene'], 'rb')
        else:
            f = open(options['indexGene'], 'rb')

        col = []
        synonymColumns = ["previous symbols", "synonyms",
                          "approved name",
                          "accession numbers", "locus type"]
        dbxrefColumns = ["entrez", "ensembl", "mgi", "refseq"]
        nn = 0
        n = 0
        data = ''

        try:
            for line in f:
                parts = re.split('\t', line.decode("utf-8").rstrip())
                ''' Use table header to identify column names '''
                if(len(col) == 0):
                    for part in parts:
                        col.append(part.lower()
                                   .replace(' gene id', '')
                                   .replace(' ids', '')
                                   .replace('mouse genome database id', 'mgi'))
                    continue

                col_dict = {}
                for idx, part in enumerate(parts):
                    if part != '':
                        col_dict[col[idx]] = part

                if("status" in col_dict and col_dict["status"] == 'Approved'):
                    print("loading... "+col_dict["approved symbol"])

                    dbxref_data = {}
                    for dbType in dbxrefColumns:
                        if(dbType in col_dict and
                           col_dict[dbType].strip() != ''):
                            # split and strip
                            dbxrefs = re.sub(r'\s', '',
                                             col_dict[dbType]
                                             .strip()).split(',')
                            for acc in dbxrefs:
                                dbxref_data[dbType] = acc

                    synonym_data = []
                    for synType in synonymColumns:
                        if(synType in col_dict):
                            syns = col_dict[synType].strip().split(',')
                            for syn in syns:
                                synonym_data.append(syn)

                    data += '{"index": {"_id": "%s"}}\n' % nn
                    data += json.dumps({"gene_symbol":
                                        col_dict["approved symbol"],
                                        "organism": org,
                                        "hgnc": col_dict["hgnc id"][5:],
                                        "dbxrefs": dbxref_data,
                                        "synonyms": synonym_data
                                        })+'\n'
                    nn += 1
                    n += 1

                    if(n > 5000):
                        n = 0
                        response = requests.put(settings
                                                .ELASTICSEARCH_URL+'/' +
                                                indexName+'/gene/_bulk',
                                                data=data)
                        data = ''
        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                    indexName+'/gene/_bulk', data=data)
            return response

    ''' Create the mapping for gene names indexing '''
    def create_genename_index(self, **options):
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "genename"

        props = {"properties":
                 {"gene_symbol": {"type": "string", "boost": 4},
                  "organism": {"type": "string"},
                  "hgnc": {"type": "string"},
                  "dbxrefs": {"properties":
                              {"dbname": {"type": "string"},
                               "accession": {"type": "string"}
                               }
                              },
                  "synonyms": {"type": "string"}
                  }
                 }

        data = {"mappings": {indexName: props}}
        response = requests.put(settings.ELASTICSEARCH_URL+'/'+indexName+'/',
                                data=json.dumps(data))
        print (response.text)
        return
