from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX
import requests
import time
import json
from elastic.elastic_settings import ElasticSettings


@override_settings(SEARCH={'default': {'IDX': {'MARKER_IDX': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    time.sleep(1)


@override_settings(SEARCH={'default': {'IDX': {'MARKER_IDX': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(SEARCH={'default': {'IDX': {'MARKER_IDX': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
class ElasticViewsTest(TestCase):

    def test_server(self):
        ''' Test elasticsearch server is running and status '''
        try:
            resp = requests.get(ElasticSettings.url() + '/_cluster/health/')
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
        ''' Test a single SNP elastic '''
        resp = self.client.get('/search/rs2476601/')
        self.assertEqual(resp.status_code, 200)
#         print(resp.context)
        self.assertTrue('data' in resp.context)
        snp = resp.context['data'][0]
        self._SNPtest(snp)

    def test_snp_wildcard(self):
        ''' Test a wild card elastic '''
        resp = self.client.get('/search/rs3*/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for snp in resp.context['data']:
            self._SNPtest(snp)

    def test_ajax_search(self):
        ''' Test the elastic count '''
        self._check_ajax('/search/rs%2A/db/')
        self._check_ajax('/search/1%3A1-2880054/db/')

    def _check_ajax(self, url_path):
        resp = self.client.get(url_path+ElasticSettings.idx(name='MARKER_IDX')+'/count')
        self.assertEqual(resp.status_code, 200)
        json_string = str(resp.content, encoding='utf8')
        data = json.loads(json_string)
        self.assertTrue('count' in data)
        data = {'from': 20, 'size': 10}
        resp = self.client.post(url_path+ElasticSettings.idx(name='MARKER_IDX')+'/show', data)
        self.assertEqual(resp.status_code, 200)

    def test_range(self):
        ''' Test a range query '''
        resp = self.client.get('/search/1:10019-113834947/db/'+ElasticSettings.idx(name='MARKER_IDX'))
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

# NEED region test data
#     def test_region_index(self):
#         ''' Test Region Index '''
#         index_name = ElasticSettings.getattr(name='REGION_IDX')
#         try:
#             # Test if region index exists
#             resp = requests.head(ElasticSettings.url() + '/' + index_name)
#             self.assertEqual(resp.status_code, 200, "Region Index " + index_name + "exists")
#             # Test if type region exists
#             index_type = 'region'
#             resp = requests.head(ElasticSettings.url() +
#                                  '/' + index_name +
#                                  '/' + index_type)
#             self.assertEqual(resp.status_code, 200, "Region Index: " +
#                              index_name + " and Region Index Type: " +
#                              index_type + " exists")
#         except requests.exceptions.Timeout:
#             self.assertTrue(False, 'timeout exception')
#         except requests.exceptions.TooManyRedirects:
#             self.assertTrue(False, 'too many redirects exception')
#         except requests.exceptions.ConnectionError:
#             self.assertTrue(False, 'request connection exception')
#         except requests.exceptions.RequestException:
#             self.assertTrue(False, 'request exception')
#
#     def test_region_search(self):
#         ''' Test a single Region elastic '''
#         resp = self.client.get('/elastic/22q12.2/')
#         self.assertEqual(resp.status_code, 200)
#         self.assertTrue('data' in resp.context)
#         region = resp.context['data'][0]
#         self._RegionTest(region)
#
#     def test_region_wildcard(self):
#         ''' Test a wild card elastic '''
#         resp = self.client.get('/elastic/22q12*/')
#         self.assertEqual(resp.status_code, 200)
#         self.assertTrue('data' in resp.context)
#
#         for region in resp.context['data']:
#             self._RegionTest(region)
#
#     def _RegionTest(self, region):
#         ''' Test the elements of a Region result '''
#         self.assertTrue(region['seqid'])
#         self.assertTrue(region['type'])
#         self.assertTrue(region['source'])
#         self.assertTrue(region['start'])
#         self.assertTrue(region['end'])
