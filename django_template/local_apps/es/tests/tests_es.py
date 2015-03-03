from django.test import TestCase
from django.conf import settings
import requests
import unittest


class EsTest(TestCase):
    '''
    Test elasticsearch server is running and status
    '''
    def test_es(self):
        try:
            resp = requests.get(settings.ELASTICSEARCH_URL +
                                '/_cluster/health/'+settings.MARKERDB)
            self.assertEqual(resp.status_code, 200, "Health page status code")
            self.assertFalse(resp.json()['status'] == 'red',
                             'Health report - red')
        except requests.exceptions.Timeout:
            self.assertTrue(False, 'timeout exception')
        except requests.exceptions.TooManyRedirects:
            self.assertTrue(False, 'too many redirects exception')
        except requests.exceptions.ConnectionError:
            self.assertTrue(False, 'request connection exception')
        except requests.exceptions.RequestException:
            self.assertTrue(False, 'request exception')

    '''
    Test a single SNP search
    '''
    def test_snp_search(self):
        resp = self.client.get('/search/rs333/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)
        snp = resp.context['data'][0]
        self._SNPtest(snp)

    '''
    Test a wild card search
    '''
    def test_snp_wildcard(self):
        resp = self.client.get('/search/rs33311*/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for snp in resp.context['data']:
            self._SNPtest(snp)

    '''
    Test a range query
    '''
    def test_range(self):
        resp = self.client.get('/search/chr4:10000-10050/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for snp in resp.context['data']:
            self._SNPtest(snp)

    '''
    Test the elements of a SNP result
    '''
    def _SNPtest(self, snp):
        self.assertTrue(snp['pos'])
        self.assertTrue(snp['id'])
        self.assertTrue(snp['ref'])
        self.assertTrue(snp['alt'])
        self.assertTrue(snp['src'])

        self.assertTrue(isinstance(snp['pos'], int))

    '''
    Test Region Index
    '''
    def test_region_index(self):
        index_name = settings.REGIONDB
        try:
            # Test if region index exists
            resp = requests.head(settings.ELASTICSEARCH_URL + '/' + index_name)
            self.assertEqual(resp.status_code, 200, "Region Index " +
                             index_name + "exists")
            # Test if type region exists
            index_type = 'region'
            resp = requests.head(settings.ELASTICSEARCH_URL +
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

    '''
    Dummy Test to skip
    '''
    @unittest.skip("demonstrating skipping")
    def test_dummy_test_skipping(self):
        pass

    '''
    Test a single Region search
    '''
    def test_region_search(self):
        resp = self.client.get('/search/22q12.2/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)
        region = resp.context['data'][0]
        self._RegionTest(region)

    '''
    Test a wild card search
    '''
    def test_region_wildcard(self):
        resp = self.client.get('/search/22q12*/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('data' in resp.context)

        for region in resp.context['data']:
            self._RegionTest(region)

    '''
    Test the elements of a Region result
    '''
    def _RegionTest(self, region):
        self.assertTrue(region['seqid'])
        self.assertTrue(region['type'])
        self.assertTrue(region['source'])
        self.assertTrue(region['start'])
        self.assertTrue(region['end'])
