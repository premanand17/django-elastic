from django.test import TestCase
from elastic.elastic_settings import ElasticSettings, ElasticUrl
from elastic.exceptions import SettingsError
from django.test.utils import override_settings
from elastic.tests.settings_idx import OVERRIDE_SETTINGS, OVERRIDE_SETTINGS3, OVERRIDE_SETTINGS4,\
    IDX
from django.core.management import call_command
from elastic.search import Search, ElasticQuery
import requests
from elastic.query import Query, Filter


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    Search.index_refresh(IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


class ElasticSettingsTest(TestCase):

    @override_settings(ELASTIC=OVERRIDE_SETTINGS3)
    def test_get_label(self):
        ''' Test method for getting the index or type label in the settings. '''
        self.assertRaises(SettingsError, ElasticSettings.get_label, 'ABC')
        self.assertTrue(isinstance(ElasticSettings.get_label('MARKER', idx_type='MARKER', label='description'), str))
        self.assertTrue(isinstance(ElasticSettings.get_label('MARKER'), str))

    @override_settings(ELASTIC=OVERRIDE_SETTINGS4)
    def test_url_rotate(self):
        ''' Test the url rotates from http://xxx:9200 to correct url. '''
        query = ElasticQuery.filtered(Query.term("seqid", 1), Filter(Query.term("id", "rs768019142")))
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total == 1, "Elastic filtered query retrieved marker")
        Search.index_exists('test', 'test2')
        ElasticUrl.URL_INDEX = 0  # reset
