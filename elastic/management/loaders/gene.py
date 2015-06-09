''' Loader for gene data. '''
import re
from elastic.search import Search
from elastic.management.loaders.loader import Loader
from elastic.management.loaders.mapping import MappingProperties
from elastic.management.loaders.utils import GFF
import sys
import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class GeneManager(Loader):

    def load_genename(self, **options):
        '''
        Create index based on genenames.org download file for names
        (http://www.genenames.org/cgi-bin/download).
        The file is assumed to include the following columns:
        hgnc id, approved symbol, status, locus type, previous symbols
        synonyms, entrez gene id, ensembl gene id
        '''
        idx_name = self.get_index_name(**options)
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
        idx_n = 0
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
                    logger.debug("loading... "+col_dict["approved symbol"])

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

                    data += '{"index": {"_id": "%s"}}\n' % idx_n
                    data += json.dumps({"gene_symbol":
                                        col_dict["approved symbol"],
                                        "organism": org,
                                        "hgnc": col_dict["hgnc id"][5:],
                                        "dbxrefs": dbxref_data,
                                        "synonyms": synonym_data
                                        })+'\n'
                    idx_n += 1
                    n += 1

                    if(n > 5000):
                        n = 0
                        self.bulk_load(idx_name, 'gene', data)
                        data = ''
        finally:
            self.bulk_load(idx_name, 'gene', data)

    def update_gene(self, **options):
        ''' Use gene span GFF coordinates to add coordinates '''
        idx_name = self.get_index_name(**options)
        if options['build']:
            build = options['build']
        else:
            print("Please supply a build version!")
            sys.exit()

        f = self.open_file_to_load('indexGeneGFF', **options)
        line_num = 0
        auto_num = 1
        json_data = ''
        chunk = 1000

        try:
            for line in f:
                line = line.decode("utf-8").rstrip()
                if(line.startswith("##")):
                    continue
                gff = GFF(line)

                context = self._call_elasticsearch(gff.attrs["Name"], ["gene_symbol"], idx_name)
                if context["total"] != 1:
                    context = self._call_elasticsearch(gff.attrs["Name"], ["synonyms"], idx_name)
                if context["total"] != 1:
                    print ("IGNORE "+gff.attrs["Name"]+" "+gff.attrs["biotype"])
                    continue

                gdata = context["data"][0]
                if "entrezGene_id" in gff.attrs and "entrez" in gdata["dbxrefs"]:
                    if gff.attrs["entrezGene_id"] != gdata["dbxrefs"]["entrez"]:
                        logger.debug("Entrez ID not matching "+gff.attrs["Name"] + " " +
                                     gff.attrs["biotype"] + " Entrez:" +
                                     gff.attrs["entrezGene_id"] + " != " +
                                     gdata["dbxrefs"]["entrez"])
                        continue

                doc_data = {"update": {"_id": gdata["idx_id"], "_type": "gene",
                                       "_index": idx_name, "_retry_on_conflict": 3}}
                json_data += json.dumps(doc_data) + '\n'
                doc_data = {"doc": {"featureloc":
                                    {"start": gff.start,
                                     "end": gff.end,
                                     "seqid": gff.seqid,
                                     "build": build
                                     },
                                    "biotype": gff.attrs["biotype"]
                                    }
                            }
                json_data += json.dumps(doc_data) + '\n'
                line_num += 1
                auto_num += 1
                if(line_num > chunk):
                    line_num = 0
                    print('.', end="", flush=True)
                    self.bulk_load(idx_name, 'gene', json_data)
                    json_data = ''
        finally:
            self.bulk_load(idx_name, 'gene', json_data)

    def _call_elasticsearch(self, name, fields, indexName):
        ''' Call elasticsearch '''
        elastic = Search.field_search_query(name, fields=fields, search_from=0,
                                            size=20, idx=indexName)
        return elastic.get_result()

    def _create_mapping(self, **options):
        ''' Create the mapping for gene names indexing '''
        props = MappingProperties("gene")
        props.add_property("gene_symbol", "string", analyzer="full_name") \
             .add_property("biotype", "string") \
             .add_property("synonyms", "string", analyzer="full_name") \
             .add_property("hgnc", "string") \
             .add_property("dbxrefs", "object") \
             .add_property("organism", "string")

        featureloc_props = MappingProperties("featureloc")
        featureloc_props.add_property("start", "integer") \
                        .add_property("end", "integer") \
                        .add_property("seqid", "string") \
                        .add_property("build", "string")
        props.add_properties(featureloc_props)

        ''' create index and add mapping '''
        self.mapping(props, 'gene', analyzer=self.KEYWORD_ANALYZER, **options)
