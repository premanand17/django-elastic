from django.test import TestCase
from django.conf import settings
import requests
#from django.views.decorators.cache import cache_page

# models test
class EsTest(TestCase):

    '''
    Test elasticsearch server is running and status
    '''
    def test_es(self):
        resp = requests.get(settings.ELASTICSEARCH_URL+'/_cluster/health')
        self.assertEqual(resp.status_code, 200, "Health page status code")
        self.assertFalse(resp.json()['status'] == 'red', "Elasticsearch status check")

    def test_snp_search(self):
        resp = self.client.get('/search/rs333/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)
        snp = resp.context['data'][0]
        self._SNPtest(snp)
        
    def test_snp_wildcard(self):
        resp = self.client.get('/search/wildcard/rs33311w/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for snp in resp.context['data']:
            self._SNPtest(snp)
            
    def _SNPtest(self, snp):
        self.assertTrue(snp['POS'])
        self.assertTrue(snp['ID'])
        self.assertTrue(snp['REF'])
        self.assertTrue(snp['ALT'])
        self.assertTrue(snp['SRC'])
