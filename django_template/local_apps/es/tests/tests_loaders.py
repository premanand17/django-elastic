from django.test import TestCase
from django.core.management import call_command
from django_template import settings
from es.tests.settings_idx import IDX
import requests
import time
import random
import string


class ElasticLoadersTest(TestCase):

    def test_disease_loader(self):
        ''' Test disease loader '''
        options = IDX['DISEASE']
        index_name = IDX['DISEASE']['indexName']
        call_command('index_search', **options)
        time.sleep(2)
        self._check_index(index_name, 'disease', 19)
        self._remove(index_name)

    def test_marker_loader(self):
        ''' Test disease loader '''
        options = IDX['MARKER']
        index_name = IDX['MARKER']['indexName']
        call_command('index_search', **options)
        time.sleep(2)
        self._check_index(index_name, 'marker')
        self._remove(index_name)

    def _check_index(self, index_name, index_type, count=None):
        self._check(settings.ELASTICSEARCH_URL + '/' + index_name)
        response = self._check(settings.ELASTICSEARCH_URL + '/' + index_name +
                               '/' + index_type + '/_count')
        if count is not None:
            self.assertEqual(response.json()['count'], 19,
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

    def _remove(self, index_name):
        response = requests.delete(settings.ELASTICSEARCH_URL +
                                   '/' + index_name)
        self.assertEqual(response.status_code, 200, "Index " +
                         index_name + " exists")

    def _id_generator(self, size=6,
                      chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
