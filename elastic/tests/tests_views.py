''' Test for view. '''
from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, OVERRIDE_SETTINGS2
from elastic.elastic_settings import ElasticSettings
from elastic.search import Search
import requests
import json
import time


@override_settings(ELASTIC=OVERRIDE_SETTINGS2)
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])

    # wait for the elastic load to finish
    Search.index_refresh(IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS2)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS2)
class ElasticViewsTest(TestCase):

    def test_server(self):
        ''' Test elasticsearch server is running and status '''
        try:
            url = ElasticSettings.url() + '/_cluster/health/'
            resp = requests.get(url)
            self.assertEqual(resp.status_code, 200, "Health page status code")
            if resp.json()['status'] == 'red':  # allow status to recover if necessary
                for _ in range(3):
                    time.sleep(1)
                    resp = requests.get(url)
                    if resp.json()['status'] != 'red':
                        break
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
        resp = self.client.get('/search/rs2476601/db/'+ElasticSettings.idx('MARKER'))
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('total' in resp.context)
        self.assertTrue(resp.context['total'] == 1)

    def test_snp_wildcard(self):
        ''' Test a wild card elastic '''
        resp = self.client.get('/search/rs3*/db/'+ElasticSettings.idx('MARKER'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('total' in resp.context)
        self.assertTrue(resp.context['total'] >= 1)

    def test_ajax_search(self):
        ''' Test the elastic count '''
        self._check_ajax('/search/rs%2A/db/')
        self._check_ajax('/search/1%3A1-2880054/db/')

    def _check_ajax(self, url_path):
        resp = self.client.get(url_path+ElasticSettings.idx(name='MARKER')+'/count')
        self.assertEqual(resp.status_code, 200)
        json_string = str(resp.content, encoding='utf8')
        data = json.loads(json_string)
        self.assertTrue('count' in data)
        data = {'from': 20, 'size': 10}
        resp = self.client.post(url_path+ElasticSettings.idx(name='MARKER')+'/show', data)
        self.assertEqual(resp.status_code, 200)

    def test_range(self):
        ''' Test a range query '''
        resp = self.client.get('/search/1:10019-113834947/db/'+ElasticSettings.idx(name='MARKER'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('total' in resp.context)
        self.assertTrue(resp.context['total'] >= 1)
