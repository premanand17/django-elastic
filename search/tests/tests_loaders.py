from django.test import TestCase
from django.core.management import call_command
from search.tests.settings_idx import IDX, IDX_UPDATE
from django.conf import settings
import requests
import time
from search.management.loaders.Utils import GFF, GFFError


def setUpModule():
    ''' Run the index loading script to create test indices '''
    for idx_kwargs in IDX.values():
        call_command('index_search', **idx_kwargs)
    time.sleep(2)
    for idx_kwargs in IDX_UPDATE.values():
        call_command('index_search', **idx_kwargs)


def tearDownModule():
    ''' Remove loaded test indices '''
    for key in IDX:
        requests.delete(settings.SEARCH_ELASTIC_URL +
                        '/' + IDX[key]['indexName'])


class ElasticLoadersTest(TestCase):

    def test_disease_loader(self):
        ''' Test disease loader '''
        index_name = IDX['DISEASE']['indexName']
        self._check_index(index_name, 'disease', 19)

    def test_marker_loader(self):
        ''' Test disease loader '''
        index_name = IDX['MARKER']['indexName']
        self._check_index(index_name, 'marker')

    def test_utils(self):
        line = "chr22\tt1dbase\tvariant\t37191071\t37191071\t.\t+\t.\tName=rs229533;region_id=36"
        gff = GFF(line)
        attrs = gff.getAttributes()
        self.assertTrue('Name' in attrs, "GFF attributes parse")
        line = '1\thavana\texon\t137682\t137965\t.\t-\t.\tgene_id "ENSG00000269981"; gene_version "1";'
        gff = GFF(line, key_value_delim=' ')
        attrs = gff.getAttributes()
        self.assertTrue('gene_id' in attrs, "GFF attributes parse")

        # check for gff errors
        line = "chr22\tt1dbase\tvariant\t37191071\t37191071\t.\t+\t."
        self.assertRaises(GFFError, GFF, line=line)

    def _check_index(self, index_name, index_type, count=None):
        self._check(settings.SEARCH_ELASTIC_URL + '/' + index_name)
        response = self._check(settings.SEARCH_ELASTIC_URL + '/' + index_name +
                               '/' + index_type + '/_count')
        if count is not None:
            self.assertEqual(response.json()['count'], count,
                             "Index count "+str(response.json()['count']))

    def _check(self, url):
        try:
            response = requests.get(url)
            self.assertEqual(response.status_code, 200, "Index " +
                             url + " exists")
            return response
        except requests.exceptions.Timeout:
            self.assertTrue(False, 'timeout exception')
        except requests.exceptions.TooManyRedirects:
            self.assertTrue(False, 'too many redirects exception')
        except requests.exceptions.ConnectionError:
            self.assertTrue(False, 'request connection exception')
        except requests.exceptions.RequestException:
            self.assertTrue(False, 'request exception')
