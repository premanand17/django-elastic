''' Test for TastyPie resources (L{tastypie.ElasticResource}) and constructing
queries L{elastic_model}. '''
from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, OVERRIDE_SETTINGS
from elastic.elastic_settings import ElasticSettings
from elastic.utils import ElasticUtils
from elastic.search import Search, ElasticQuery
import requests
from elastic.query import Query, BoolQuery
from elastic.result import Document


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['GFF_GENERIC'])
    Search.index_refresh(IDX['GFF_GENERIC']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['GFF_GENERIC']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class UtilsTest(TestCase):

    def test_get_rdm_feature_id(self):
        ''' Test get random feature id. '''
        idx = IDX['GFF_GENERIC']['indexName']
        idx_type = IDX['GFF_GENERIC']['indexType']
        doc_id = ElasticUtils.get_rdm_feature_id(idx, idx_type)

        self.assertTrue(isinstance(doc_id, str), 'Document id')
        docs = Search(ElasticQuery(Query.ids(doc_id)), idx=idx).search().docs
        self.assertTrue(len(docs) == 1, 'Document retrieved')

    def test_get_rdm_docs(self):
        ''' Test get random document(s). '''
        idx = IDX['GFF_GENERIC']['indexName']
        idx_type = IDX['GFF_GENERIC']['indexType']
        docs = ElasticUtils.get_rdm_docs(idx, idx_type)
        self.assertEqual(len(docs), 1, 'Retrieved one document')
        self.assertTrue(isinstance(docs[0], Document), 'Document type')

    def test_get_rdm_feature_ids(self):
        ''' Test get random feature ids. '''
        idx = IDX['GFF_GENERIC']['indexName']
        idx_type = IDX['GFF_GENERIC']['indexType']
        ids = ElasticUtils.get_rdm_feature_ids(idx, idx_type, size=2)
        self.assertEqual(len(ids), 2, 'Retrieved one document')

    def test_search_count(self):
        ''' Test index and search counts. '''
        idx = IDX['GFF_GENERIC']['indexName']
        idx_type = IDX['GFF_GENERIC']['indexType']
        count1 = ElasticUtils.get_docs_count(idx, idx_type)
        self.assertGreater(count1, 0, 'index count')
        search_query = ElasticQuery(BoolQuery(must_not_arr=[Query.term('seqid', 'chr1')]))
        count2 = ElasticUtils.get_docs_count(idx, idx_type, search_query=search_query)
        self.assertGreater(count1, count2, 'search query count')
