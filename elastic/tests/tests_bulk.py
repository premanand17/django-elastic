''' '''
from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, OVERRIDE_SETTINGS
from elastic.elastic_settings import ElasticSettings
from elastic.search import Delete, ElasticQuery, Search
from elastic.query import Query
import requests


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    # wait for the elastic load to finish
    Search.index_refresh(IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


class BulkApiTest(TestCase):

    def test_delete_docs_by_query(self):
        ''' Test deleting docs using a query. '''
        idx = IDX['MARKER']['indexName']
        query = ElasticQuery(Query.match_all())
        elastic = Search(query, idx=idx)
        hits_total1 = elastic.get_count()['count']
        self.assertGreater(hits_total1, 0, "contains documents")

        # delete single doc
        Delete.docs_by_query(idx, query=Query.term("id", "rs2476601"))
        Search.index_refresh(idx)
        hits_total2 = elastic.get_count()['count']
        self.assertEquals(hits_total2, hits_total1-1, "contains documents")

        # delete remaining docs
        Delete.docs_by_query(idx, 'marker')
        Search.index_refresh(idx)
        self.assertEquals(elastic.get_count()['count'], 0, "contains no documents")
