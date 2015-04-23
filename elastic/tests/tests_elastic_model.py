from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX
import requests
from elastic.elastic_model import Elastic, BoolQuery, Query, ElasticQuery, \
    RangeQuery, OrFilter, AndFilter, Filter, NotFilter, TermsFilter
from elastic.elastic_settings import ElasticSettings
import time


@override_settings(ELASTIC={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                        'ELASTIC_URL': ElasticSettings.url()}})
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    time.sleep(2)


@override_settings(ELASTIC={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
                                        'ELASTIC_URL': ElasticSettings.url()}})
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(ELASTIC={'default': {'IDX': {'DEFAULT': IDX['MARKER']['indexName']},
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

    def test_bool_filtered_query(self):
        ''' Test building and running a filtered boolean query. '''
        query_bool = BoolQuery()
        query_bool.must([Query.term("id", "rs373328635")])
        query_bool.must_not([Query.term("seqid", 2)])
        query_bool.should(RangeQuery("start", gte=10054))
        query_bool.should([RangeQuery("start", gte=10050)])
        query = ElasticQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid"])
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic filtered query retrieved marker (rs373328635)")

    def test_or_filtered_query(self):
        ''' Test building and running a filtered query. '''
        query_bool = BoolQuery(must_arr=[RangeQuery("start", lte=1),
                                         RangeQuery("end", gte=100000)])
        or_filter = OrFilter(RangeQuery("start", gte=1, lte=100000))
        or_filter.extend(query_bool)
        query = ElasticQuery.filtered(Query.term("seqid", 1), or_filter)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] >= 1, "Elastic filtered query retrieved marker(s)")

    def test_and_filtered_query(self):
        ''' Test building and running a filtered query. '''
        query_bool = BoolQuery(must_arr=[RangeQuery("start", gte=1)])
        and_filter = AndFilter(query_bool)
        query = ElasticQuery.filtered(Query.term("seqid", 1), and_filter)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] >= 1, "Elastic filtered query retrieved marker(s)")

    def test_not_filtered_query(self):
        ''' Test building and running a filtered query. '''
        not_filter = NotFilter(RangeQuery("start", lte=10000))
        query = ElasticQuery.filtered(Query.term("seqid", 1), not_filter)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] >= 1, "Elastic filtered query retrieved marker(s)")

    def test_term_filtered_query(self):
        ''' Test filtered query with a term filter. '''
        query = ElasticQuery.filtered(Query.term("seqid", 1), Filter(Query.term("id", "rs373328635")))
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] >= 1, "Elastic filtered query retrieved marker(s)")

    def test_terms_filtered_query(self):
        ''' Test filtered query with a terms filter. '''
        terms_filter = TermsFilter.get_terms_filter("id", ["rs2476601", "rs373328635"])
        query = ElasticQuery.filtered(Query.term("seqid", 1), terms_filter)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] >= 1, "Elastic filtered query retrieved marker(s)")

    def test_string_query(self):
        ''' Test building and running a string query. '''
        query = ElasticQuery.query_string("rs2476601", fields=["id"])
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic string query retrieved marker (rs2476601)")

    def test_match_query(self):
        ''' Test building and running a match query. '''
        query = ElasticQuery.query_match("id", "rs2476601")
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic string query retrieved marker (rs2476601)")

    def test_term_query(self):
        ''' Test building and running a match query. '''
        query = ElasticQuery(Query.term("id", "rs2476601"))
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic string query retrieved marker (rs2476601)")

        query = ElasticQuery(Query.term("seqid", "1", boost=3.0))
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] > 1, "Elastic string query retrieved marker (rs2476601)")

    def test_terms_query(self):
        ''' Test building and running a match query. '''
        query = ElasticQuery(Query.terms("id", ["rs2476601", "rs373328635"]))
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 2, "Elastic string query retrieved marker (rs2476601)")

    def test_bool_query(self):
        query_bool = BoolQuery(must_arr=Query.term("id", "rs373328635"))
        query = ElasticQuery.bool(query_bool)
        elastic = Elastic(query, db=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_result()['total'] == 1, "Elastic string query retrieved marker (rs373328635)")
