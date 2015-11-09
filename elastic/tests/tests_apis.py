''' '''
from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, OVERRIDE_SETTINGS
from elastic.elastic_settings import ElasticSettings
from elastic.search import Bulk, Delete, ElasticQuery, Search, Update
from elastic.query import Query
import requests
import json


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class UpdateApiTest(TestCase):

    def setUp(self):
        ''' Load test indices (marker) '''
        call_command('index_search', **IDX['MARKER'])
        # wait for the elastic load to finish
        Search.index_refresh(IDX['MARKER']['indexName'])

    def test_update_doc(self):
        ''' Update with a partial document. '''
        idx = IDX['MARKER']['indexName']
        docs = Search(ElasticQuery(Query.term("id", "rs2476601"), sources=['id']), idx=idx).search().docs
        self.assertEquals(len(docs), 1, "rs2476601 document")
        update_field = {"doc": {"start": 100, "end": 200}}
        Update.update_doc(docs[0], update_field)
        Search.index_refresh(IDX['MARKER']['indexName'])
        docs = Search(ElasticQuery(Query.term("id", "rs2476601")), idx=idx).search().docs
        self.assertEquals(len(docs), 1, "rs2476601 document")
        self.assertEquals(getattr(docs[0], 'start'), 100, "rs2476601 start")
        self.assertEquals(getattr(docs[0], 'end'), 200, "rs2476601 end")


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class BulkApiTest(TestCase):

    def set_up(self):
        ''' Load test indices (marker) '''
        call_command('index_search', **IDX['MARKER'])
        # wait for the elastic load to finish
        Search.index_refresh(IDX['MARKER']['indexName'])

    def test_delete_docs_by_query(self):
        ''' Test deleting docs using a query. '''
        self.set_up()
        idx = IDX['MARKER']['indexName']
        elastic = Search(ElasticQuery(Query.match_all()), idx=idx)
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

    def test_bulk(self):
        ''' Test the Bulk.load(). '''
        self.set_up()
        idx = IDX['MARKER']['indexName']
        elastic = Search(ElasticQuery(Query.match_all()), idx=idx)
        hits_total1 = elastic.get_count()['count']

        json_data = '{"index": {"_index": "%s", "_type": "%s"}}\n' % \
                    (idx, 'marker')
        json_data += json.dumps({"alt": "G", "start": 946, "seqid": "1", "filter": ".",
                                 "ref": "A", "id": "rsXXXXX", "qual": ".", "info": "RS=XXXXX"})
        resp = Bulk.load(idx, '', json_data)
        self.assertNotEquals(resp.status_code, 200)

        # note: needs a trailing line return to work
        Bulk.load(idx, '', json_data + '\n')
        Search.index_refresh(idx)
        hits_total2 = elastic.get_count()['count']
        self.assertEquals(hits_total2, hits_total1+1, "contains documents")
