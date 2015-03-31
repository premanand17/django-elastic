import os

SEARCH_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SEARCH_TEST_DATA_PATH = os.path.join(SEARCH_BASE_DIR, 'tests/data/')

IDX = {'GENE': {'indexName': 'test__gene', 'indexGene': SEARCH_TEST_DATA_PATH+'genenames.org.test.txt.gz'},
       'DISEASE': {'indexName': 'test__disease', 'indexDisease': SEARCH_TEST_DATA_PATH+'disease.list'},
       'MARKER': {'indexName': 'test__marker', 'indexSNP': SEARCH_TEST_DATA_PATH+'dbsnp142_test.vcf.gz'},
       'GFF_GENERIC': {'indexName': 'test__gff', 'indexType': 'gff', 'indexGFF': SEARCH_TEST_DATA_PATH+'test.gff.gz'},
       'GTF_GENERIC': {'indexName': 'test__gtf', 'indexType': 'gtf', 'indexGFF': SEARCH_TEST_DATA_PATH+'test.gtf.gz',
                       'isGTF': True},
       }
