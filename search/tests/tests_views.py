from django.test import TestCase, override_settings
from django.conf import settings
from django.core.management import call_command
from search.tests.settings_idx import IDX
import requests
import time


@override_settings(SEARCH_MARKERDB=IDX['MARKER']['indexName'])
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])


@override_settings(SEARCH_MARKERDB=IDX['MARKER']['indexName'])
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(settings.SEARCH_ELASTIC_URL + '/' + IDX['MARKER']['indexName'])


@override_settings(SEARCH_MARKERDB=IDX['MARKER']['indexName'])
class ElasticViewsTest(TestCase):

    def test_server(self):
        ''' Test elasticsearch server is running and status '''
        try:
            resp = requests.get(settings.SEARCH_ELASTIC_URL + '/_cluster/health/')
            self.assertEqual(resp.status_code, 200, "Health page status code")
            self.assertFalse(resp.json()['status'] == 'red', 'Health report - red')
        except requests.exceptions.Timeout:
            self.assertTrue(False, 'timeout exception')
        except requests.exceptions.TooManyRedirects:
            self.assertTrue(False, 'too many redirects exception')
        except requests.exceptions.ConnectionError:
            self.assertTrue(False, 'request connection exception')
        except requests.exceptions.RequestException:
            self.assertTrue(False, 'request exception')

    def test_snp_search(self):
        ''' Test a single SNP search '''
        time.sleep(1)
        resp = self.client.get('/search/rs2476601/')
        self.assertEqual(resp.status_code, 200)
#         print(resp.context)
        self.assertTrue('data' in resp.context)
        snp = resp.context['data'][0]
        self._SNPtest(snp)

    def test_snp_wildcard(self):
        ''' Test a wild card search '''
        resp = self.client.get('/search/rs3*/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for snp in resp.context['data']:
            self._SNPtest(snp)

    def test_range(self):
        ''' Test a range query '''
        resp = self.client.get('/search/chr1:10600-10650/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for snp in resp.context['data']:
            self._SNPtest(snp)

    def _SNPtest(self, snp):
        ''' Test the elements of a SNP result '''
        self.assertTrue(snp['start'])
        self.assertTrue(snp['id'])
        self.assertTrue(snp['ref'])
        self.assertTrue(snp['alt'])
        self.assertTrue(snp['seqid'])

        self.assertTrue(isinstance(snp['start'], int))

    def test_region_index(self):
        ''' Test Region Index '''
        index_name = settings.SEARCH_REGIONDB
        try:
            # Test if region index exists
            resp = requests.head(settings.SEARCH_ELASTIC_URL + '/' + index_name)
            self.assertEqual(resp.status_code, 200, "Region Index " + index_name + "exists")
            # Test if type region exists
            index_type = 'region'
            resp = requests.head(settings.SEARCH_ELASTIC_URL +
                                 '/' + index_name +
                                 '/' + index_type)
            self.assertEqual(resp.status_code, 200, "Region Index: " +
                             index_name + " and Region Index Type: " +
                             index_type + " exists")
        except requests.exceptions.Timeout:
            self.assertTrue(False, 'timeout exception')
        except requests.exceptions.TooManyRedirects:
            self.assertTrue(False, 'too many redirects exception')
        except requests.exceptions.ConnectionError:
            self.assertTrue(False, 'request connection exception')
        except requests.exceptions.RequestException:
            self.assertTrue(False, 'request exception')

    def test_region_search(self):
        ''' Test a single Region search '''
        resp = self.client.get('/search/22q12.2/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)
        region = resp.context['data'][0]
        self._RegionTest(region)

    def test_region_wildcard(self):
        ''' Test a wild card search '''
        resp = self.client.get('/search/22q12*/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for region in resp.context['data']:
            self._RegionTest(region)

    def _RegionTest(self, region):
        ''' Test the elements of a Region result '''
        self.assertTrue(region['seqid'])
        self.assertTrue(region['type'])
        self.assertTrue(region['source'])
        self.assertTrue(region['start'])
        self.assertTrue(region['end'])
