from django.conf import settings
import os

TEST_DATA_PATH = os.path.join(settings.BASE_DIR, 'django_template/local_apps/es/tests/data/')

IDX = {'GENE': {'indexName': 'test__gene', 'indexGene': TEST_DATA_PATH+'genenames.org.test.txt.gz'},
       'DISEASE': {'indexName': 'test__disease', 'indexDisease': TEST_DATA_PATH+'disease.list'},
       'MARKER': {'indexName': 'test__marker', 'indexSNP': TEST_DATA_PATH+'dbsnp142_test.vcf.gz'},
       'GFF_GENERIC': {'indexName': 'test__gff', 'indexType': 'gff', 'indexGFF': TEST_DATA_PATH+'test.gff.gz'},
       }
