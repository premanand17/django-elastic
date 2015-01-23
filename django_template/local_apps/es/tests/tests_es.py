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
        self.assertEqual(resp.status_code, 200)
        self.assertTrue((resp.json()['status'] == 'yellow' or resp.json()['status'] == 'green'), "Elasticsearch status check")
