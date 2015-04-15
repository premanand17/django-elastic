from django.test import TestCase, override_settings
from django.core.management import call_command
from search.tests.settings_idx import IDX
import requests
from search.elastic_model import Elastic, QueryBool, Query, BuildQuery
from search.elastic_settings import ElasticSettings
import json


@override_settings(SEARCH={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])


@override_settings(SEARCH={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(SEARCH={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                       'ELASTIC_URL': ElasticSettings.url()}})
class ElasticModelTest(TestCase):

    def test_mapping(self):
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

    def test_build_query(self):
        query_bool = QueryBool()
        query_bool.must([{"term": {"id": "rs2476601"}}])
        query_bool.must_not([{"term": {"seqid": "2"}}])
        query_bool.should({"range": {"start": {"gte": 113834945}}})
        query_bool.should([{"range": {"start": {"gte": 113834944}}}])
        query = BuildQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid"])
        print("curl 'http://jenkins:9200/dbsnp142/_search?pretty=true' -d '"+json.dumps(query.query)+"'")
