''' Settings used for the tests. '''
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
       'MARKER_RS_HISTORY': {'indexName': 'test__snp_merge_'+SEARCH_SUFFIX,
                             'indexSNPMerge': SEARCH_TEST_DATA_PATH+'rs_merge_test.gz'},
       'GFF_GENERIC': {'indexName': 'test__gff_'+SEARCH_SUFFIX, 'indexType': 'gff',
                       'indexGFF': SEARCH_TEST_DATA_PATH+'test.gff.gz'},
       'GTF_GENERIC': {'indexName': 'test__gtf_'+SEARCH_SUFFIX, 'indexType': 'gtf',
                       'indexGFF': SEARCH_TEST_DATA_PATH+'test.gtf.gz', 'isGTF': True},
       'GFF_ERR': {'indexName': 'test__err__gff_'+SEARCH_SUFFIX, 'indexType': 'gff',
                   'indexGFF': SEARCH_TEST_DATA_PATH+'test_error.gff.gz'},
       'GENE_TARGET': {'indexName': 'test__gene_target_'+SEARCH_SUFFIX,
                       'indexGTarget': SEARCH_TEST_DATA_PATH+'gene_targets.tab.gz'},
       'T1D_CRITERIA': {'indexName': 'test__t1d_criteria_'+SEARCH_SUFFIX, 'indexProject': 't1dbase',
                        'indexCriteria': 'true', 'applyFilter': '1'},
       'IMB_CRITERIA': {'indexName': 'test__imb_criteria_'+SEARCH_SUFFIX, 'indexProject': 'immunobase',
                        'indexCriteria': 'true', 'applyFilter': '1'},
       'GENE_ALIAS': {'indexName': 'test__gene_alias_'+SEARCH_SUFFIX,
                      'indexAlias': SEARCH_TEST_DATA_PATH + 'alias_test_dir', 'indexFeatureType': 'gene'},
       'LOCUS_ALIAS': {'indexName': 'test__locus_alias_'+SEARCH_SUFFIX,
                       'indexAlias': SEARCH_TEST_DATA_PATH + 'alias_test_dir', 'indexFeatureType': 'locus'},
       'MARKER_ALIAS': {'indexName': 'test__marker_alias_'+SEARCH_SUFFIX,
                        'indexAlias': SEARCH_TEST_DATA_PATH + 'alias_test_dir', 'indexFeatureType': 'marker'},
       'STUDY_ALIAS': {'indexName': 'test__study_alias_'+SEARCH_SUFFIX,
                       'indexAlias': SEARCH_TEST_DATA_PATH + 'alias_test_dir', 'indexFeatureType': 'study'},
       }

IDX_UPDATE = {'GENE_UPDATE': {'indexName': 'test__gene_'+SEARCH_SUFFIX, 'build': 'GRCh38',
                              'indexGeneGFF': SEARCH_TEST_DATA_PATH+'genespan.gff.gz'},
              }

OVERRIDE_SETTINGS = \
    {'default': {'IDX':
                 {'MARKER': IDX['MARKER']['indexName'],
                  'DEFAULT': IDX['MARKER']['indexName'],
                  'GFF_GENES': IDX['GFF_GENERIC']['indexName']},
                 'ELASTIC_URL': ElasticSettings.url()}}

OVERRIDE_SETTINGS2 = \
    {'default': {'IDX':
                 {'MARKER': IDX['MARKER']['indexName'],
                  'DEFAULT': IDX['MARKER']['indexName']},
                 'ELASTIC_URL': ElasticSettings.url()}}
