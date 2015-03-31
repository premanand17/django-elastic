from django.test import TestCase, override_settings
from django.conf import settings
from django.core.management import call_command
from search.tests.settings_idx import IDX
import requests
from search.elastic_model import Elastic


@override_settings(SEARCH_MARKERDB=IDX['MARKER']['indexName'])
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])


@override_settings(SEARCH_MARKERDB=IDX['MARKER']['indexName'])
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(settings.SEARCH_ELASTIC_URL + '/' + IDX['MARKER']['indexName'])


@override_settings(SEARCH_MARKERDB=IDX['MARKER']['indexName'])
class ElasticModelTest(TestCase):

    def test_mapping(self):
        elastic = Elastic(db=settings.SEARCH_MARKERDB)
        mapping = elastic.get_mapping()
        self.assertTrue(settings.SEARCH_MARKERDB in mapping, "Database name in mapping result")
        if settings.SEARCH_MARKERDB in mapping:
            self.assertTrue("mappings" in mapping[settings.SEARCH_MARKERDB], "Mapping result found")
