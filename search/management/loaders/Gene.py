import re
import requests
from django.conf import settings
from db.management.loaders.GFF import GFF
from search.elastic_model import Elastic
from search.management.loaders.Loader import Loader
import sys
import json


class GeneManager(Loader):

    def load_genename(self, **options):
        '''
        Create index based on genenames.org download file for names
        (http://www.genenames.org/cgi-bin/download).
        The file is assumed to include the following columns:
        hgnc id, approved symbol, status, locus type, previous symbols
        synonyms, entrez gene id, ensembl gene id
        '''
        index_name = self.get_index_name(**options)
        self._create_mapping(**options)

        if options['org']:
            org = options['org']
        else:
            org = 'human'

        f = self.open_file_to_load('indexGene', **options)

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
                line = line.rstrip().decode("utf-8")
                parts = re.split('\t', line)
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
                                dbxref_data[dbType] = acc.strip()

                    synonym_data = []
                    for synType in synonymColumns:
                        if(synType in col_dict):
                            syns = col_dict[synType].strip().split(',')
                            for syn in syns:
                                synonym_data.append(syn.strip())

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
                                                .SEARCH_ELASTIC_URL+'/' +
                                                index_name+'/gene/_bulk',
                                                data=data)
                        data = ''
        finally:
            response = requests.put(settings.SEARCH_ELASTIC_URL+'/' +
                                    index_name+'/gene/_bulk', data=data)
            return response

    def update_gene(self, **options):
        ''' Use gene span GFF coordinates to add coordinates '''
        index_name = self.get_index_name(**options)

        if options['build']:
            build = options['build']
        else:
            print("Please supply a build version!")
            sys.exit()

        f = self.open_file_to_load('indexGeneGFF', **options)
        for line in f:
            line = line.decode("utf-8").rstrip()
            if(line.startswith("##")):
                continue
            gff = GFF(line)

            context = self._call_elasticsearch(gff.attrs["Name"],
                                               ["gene_symbol"], index_name)
            if context["total"] != 1:
                context = self._call_elasticsearch(gff.attrs["Name"],
                                                   ["synonyms"], index_name)
            if context["total"] != 1:
                print ("IGNORE "+gff.attrs["Name"]+" "+gff.attrs["biotype"])
                continue

            gdata = context["data"][0]
            if "entrezGene_id" in gff.attrs and "entrez" in gdata["dbxrefs"]:
                if gff.attrs["entrezGene_id"] != gdata["dbxrefs"]["entrez"]:
                    print ("Entrez ID not matching "+gff.attrs["Name"] + " " +
                           gff.attrs["biotype"] + " Entrez:" +
                           gff.attrs["entrezGene_id"] + " != " +
                           gdata["dbxrefs"]["entrez"])
                    continue

            esid = gdata["idx_id"]
            data = json.dumps({"doc":
                               {"featureloc":
                                {"start": gff.start,
                                 "end": gff.end,
                                 "seqid": gff.seqid,
                                 "build": build
                                 },
                                "biotype": gff.attrs["biotype"]}
                               })
            response = requests.post(settings.SEARCH_ELASTIC_URL+'/' +
                                     index_name+'/gene/'+esid+'/_update',
                                     data=data)
        return response

    def _call_elasticsearch(self, name, fields, indexName):
        ''' Call elasticsearch '''
        elastic = Elastic.field_search_query(name, fields, 0, 20, indexName)
        return elastic.get_result()

    def _create_mapping(self, **options):
        ''' Create the mapping for gene names indexing '''
        data = {"gene":
                {"properties":
                 {"gene_symbol": {"boost": 4, "type": "string", "analyzer": "full_name"},
                  "biotype": {"type": "string"},
                  "featureloc": {"properties": {"start": {"type": "integer"},
                                                "end": {"type": "integer"},
                                                "seqid": {"type": "string"},
                                                "build": {"type": "string"}}},
                  "synonyms": {"type": "string", "analyzer": "full_name"},
                  "hgnc": {"type": "string"},
                  "dbxrefs": {"type": "object"},
                  "organism": {"type": "string"}
                  }
                 }
                }
        ''' create index and add mapping '''
        self.mapping(data, 'gene', analyzer=self.KEYWORD_ANALYZER, **options)
