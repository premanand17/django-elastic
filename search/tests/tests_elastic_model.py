from django.test import TestCase, override_settings
from django.core.management import call_command
from search.tests.settings_idx import IDX
import requests
from search.elastic_model import Elastic, QueryBool, Query, ElasticQuery, Filter
from search.elastic_settings import ElasticSettings
import time


@override_settings(SEARCH={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    time.sleep(1)


@override_settings(SEARCH={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(SEARCH={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
class ElasticModelTest(TestCase):

    def test_mapping(self):
        ''' Test retrieving the mapping for an index. '''
        elastic = Elastic(db=ElasticSettings.idx('DEFAULT'))
        mapping = elastic.get_mapping()
        self.assertTrue(ElasticSettings.idx('DEFAULT') in mapping, "Database name in mapping result")
        if ElasticSettings.idx('DEFAULT') in mapping:
            self.assertTrue("mappings" in mapping[ElasticSettings.idx('DEFAULT')], "Mapping result found")

        # check using the index type
        mapping = elastic.get_mapping('marker')
        self.assertTrue(ElasticSettings.idx('DEFAULT') in mapping, "Database name in mapping result")

        # err check
        mapping = elastic.get_mapping('marker/xx')
        self.assertTrue('error' in mapping, "Database name in mapping result")

    def test_filtered_bool_query(self):
        ''' Test building and running a filtered boolean query. '''
        query_bool = QueryBool()
        query_bool.must([{"term": {"id": "rs373328635"}}])
        query_bool.must_not([{"term": {"seqid": "2"}}])
        query_bool.should({"range": {"start": {"gte": 10054}}})
        query_bool.should([{"range": {"start": {"gte": 10050}}}])
        query = ElasticQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid"])
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic filtered query retrieved marker (rs373328635)")

    def test_filtered_query(self):
        ''' Test building and running a filtered query. '''
        query_bool = QueryBool(must_arr=[{"range": {"start": {"lte": 1}}},
                                         {"range": {"end": {"gte": 1000000}}}])
        query_filter = Filter({"or": {"range": {"start": {"gte": 1, "lte": 1000000}}}})
        query_filter.extend("or", {"range": {"end": {"gte": 1, "lte": 1000000}}})
        query_filter.extend("or", query_bool.bool)
        query = ElasticQuery.filtered(Query.term({"seqid": 1}), query_filter)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] >= 1, "Elastic filtered query retrieved marker(s)")

    def test_string_query(self):
        ''' Test building and running a string query. '''
        query_term = "rs2476601"
        fields = ["id"]
        query = ElasticQuery.query_string(query_term, fields)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic string query retrieved marker (rs2476601)")

    def test_match_query(self):
        ''' Test building and running a match query. '''
        query = ElasticQuery.query_match("id", "rs2476601")
        elastic = Elastic(query)
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic string query retrieved marker (rs2476601)")
