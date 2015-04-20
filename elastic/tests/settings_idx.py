import os
from elastic.elastic_settings import ElasticSettings

SEARCH_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SEARCH_TEST_DATA_PATH = os.path.join(SEARCH_BASE_DIR, 'tests/data/')
SEARCH_SUFFIX = ElasticSettings.getattr('TEST')
if SEARCH_SUFFIX is None:
    SEARCH_SUFFIX = "test"

IDX = {'GENE': {'indexName': 'test__gene_'+SEARCH_SUFFIX,
                'indexGene': SEARCH_TEST_DATA_PATH+'genenames.org.test.txt.gz'},
       'DISEASE': {'indexName': 'test__disease_'+SEARCH_SUFFIX,
                   'indexDisease': SEARCH_TEST_DATA_PATH+'disease.list.gz'},
       'MARKER': {'indexName': 'test__snp_'+SEARCH_SUFFIX,
                  'indexSNP': SEARCH_TEST_DATA_PATH+'dbsnp142_test.vcf.gz'},
       'GFF_GENERIC': {'indexName': 'test__gff_'+SEARCH_SUFFIX, 'indexType': 'gff',
                       'indexGFF': SEARCH_TEST_DATA_PATH+'test.gff.gz'},
       'GTF_GENERIC': {'indexName': 'test__gtf_'+SEARCH_SUFFIX, 'indexType': 'gtf',
                       'indexGFF': SEARCH_TEST_DATA_PATH+'test.gtf.gz', 'isGTF': True},
       'GFF_ERR': {'indexName': 'test__err__gff_'+SEARCH_SUFFIX, 'indexType': 'gff',
                   'indexGFF': SEARCH_TEST_DATA_PATH+'test_error.gff.gz'},
       'GENE_TARGET': {'indexName': 'test__gene_target_'+SEARCH_SUFFIX,
                       'indexGTarget': SEARCH_TEST_DATA_PATH+'gene_targets.tab.gz'},
       }

IDX_UPDATE = {'GENE_UPDATE': {'indexName': 'test__gene_'+SEARCH_SUFFIX, 'build': 'GRCh38',
                              'indexGeneGFF': SEARCH_TEST_DATA_PATH+'genespan.gff.gz'},
              }
