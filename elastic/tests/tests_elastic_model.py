''' Test for TastyPie resources (L{tastypie.ElasticResource}) and constructing
queries L{elastic_model}. '''
from django.test import TestCase, override_settings
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, OVERRIDE_SETTINGS
from elastic.elastic_settings import ElasticSettings
from tastypie.test import ResourceTestCase
from django.core.urlresolvers import reverse
from elastic.search import Search, ElasticQuery, Highlight
from elastic.query import Query, BoolQuery, RangeQuery, Filter, TermsFilter,\
    AndFilter, NotFilter, OrFilter
from elastic.exceptions import AggregationError
from elastic.aggs import Agg, Aggs
import requests
import time


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    call_command('index_search', **IDX['GFF_GENERIC'])

    # wait for the elastic load to finish
    Search.wait_for_load(IDX['MARKER']['indexName'])
    Search.wait_for_load(IDX['GFF_GENERIC']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])
    requests.delete(ElasticSettings.url() + '/' + IDX['GFF_GENERIC']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS, ROOT_URLCONF='elastic.tests.test_urls')
class TastypieResourceTest(ResourceTestCase):
    ''' Test Tastypie interface to Elastic indices.
    Note: Overriding the ROOT_URLCONF to set up test Tastypie api that
    connects to the test indices set up for the module.
    '''

    def setUp(self):
        super(TastypieResourceTest, self).setUp()

    def safe_get_request(self, url, data=None):
        ''' Routine to allow for TastyPie to intialise if needed. '''
        resp = self.api_client.get(url, format='json', data=data)
        if len(self.deserialize(resp)['objects']) < 1:
            time.sleep(2)
            resp = self.api_client.get(url, format='json', data=data)
        return resp

    def test_list(self):
        ''' Test listing all documents. '''
        url = reverse('api_dispatch_list',
                      kwargs={'resource_name': ElasticSettings.idx('MARKER'), 'api_name': 'test'})
        resp = self.safe_get_request(url)
        self.assertValidJSONResponse(resp)
        self.assertGreater(len(self.deserialize(resp)['objects']), 0, 'Retrieved stored markers')

    def test_list_with_filtering(self):
        ''' Test getting a document using filtering. '''
        url = reverse('api_dispatch_list',
                      kwargs={'resource_name': ElasticSettings.idx('GFF_GENES'), 'api_name': 'test'})
        resp = self.safe_get_request(url, data={'attr__Name': 'rs2664170'})
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1, 'Retrieved stored markers')

        resp = self.api_client.get(url, format='json', data={'attr__xxx': 'rs2664170'})
        self.assertKeys(self.deserialize(resp), ['error'])

    def test_detail(self):
        ''' Test getting a document by primary key '''
        url = reverse('api_dispatch_detail',
                      kwargs={'resource_name': ElasticSettings.idx('MARKER'), 'api_name': 'test', 'pk': '1'})
        resp = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(resp)
        keys = ['seqid', 'start', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'resource_uri']
        self.assertKeys(self.deserialize(resp), keys)

    def test_schema(self):
        ''' Test returning the schema '''
        url = reverse('api_get_schema',
                      kwargs={'resource_name': ElasticSettings.idx('MARKER'), 'api_name': 'test'})
        resp = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(resp)


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class ElasticModelTest(TestCase):

    def test_idx_exists(self):
        ''' Test that index_exists() method. '''
        self.assertTrue(Search.index_exists(idx=ElasticSettings.idx('DEFAULT')),
                        "Index exists")
        self.assertFalse(Search.index_exists("xyz123"))

    def test_mapping(self):
        ''' Test retrieving the mapping for an index. '''
        elastic = Search(idx=ElasticSettings.idx('DEFAULT'))
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
        query_bool.must([Query.term("id", "rs373328635")]) \
                  .must_not([Query.term("seqid", 2)]) \
                  .should(RangeQuery("start", gte=10054)) \
                  .should([RangeQuery("start", gte=10050)])
        query = ElasticQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total == 1, "Elastic filtered query retrieved marker (rs373328635)")

    def test_bool_filtered_query2(self):
        ''' Test building and running a filtered boolean query. '''
        query_bool = BoolQuery()
        query_bool.should(RangeQuery("start", lte=20000)) \
                  .should(Query.term("seqid", 2)) \
                  .must(Query.term("seqid", 1))
        query_string = Query.query_string("rs373328635", fields=["id", "seqid"])
        query = ElasticQuery.filtered_bool(query_string, query_bool, sources=["id", "seqid", "start"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total == 1, "Elastic filtered query retrieved marker (rs373328635)")

    def test_bool_filtered_query3(self):
        ''' Test building and running a filtered boolean query. Note:
        ElasticQuery used to wrap query_string in a query object. '''
        query_bool = BoolQuery()
        query_bool.should(RangeQuery("start", lte=20000)) \
                  .should(Query.term("seqid", 2)) \
                  .must(Query.query_string("rs373328635", fields=["id", "seqid"]).query_wrap()) \
                  .must(Query.term("seqid", 1))

        query = ElasticQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid", "start"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total == 1, "Elastic filtered query retrieved marker (rs373328635)")

    def test_bool_filtered_query4(self):
        ''' Test building and running a filtered boolean query.
        Note: ElasticQuery used to wrap match in a query object. '''
        query_bool = BoolQuery()
        query_bool.should(RangeQuery("start", lte=20000)) \
                  .should(Query.term("seqid", 2)) \
                  .must(Query.match("id", "rs373328635").query_wrap()) \
                  .must(Query.term("seqid", 1))

        query = ElasticQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid", "start"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total == 1, "Elastic filtered query retrieved marker (rs373328635)")

    def test_bool_nested_filter(self):
        ''' Test combined Bool filter '''
        query_bool_nest = BoolQuery()
        query_bool_nest.must(Query.match("id", "rs373328635").query_wrap()) \
                       .must(Query.term("seqid", 1))

        query_bool = BoolQuery()
        query_bool.should(query_bool_nest) \
                  .should(Query.term("seqid", 2))
        query = ElasticQuery.filtered_bool(Query.match_all(), query_bool, sources=["id", "seqid", "start"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total >= 1, "Nested bool filter query")

    def test_or_filtered_query(self):
        ''' Test building and running a filtered query. '''
        highlight = Highlight(["id", "seqid"])
        query_bool = BoolQuery(must_arr=[RangeQuery("start", lte=1),
                                         RangeQuery("end", gte=100000)])
        or_filter = OrFilter(RangeQuery("start", gte=1, lte=100000))
        or_filter.extend(query_bool) \
                 .extend(Query.query_string("rs*", fields=["id", "seqid"]).query_wrap())
        query = ElasticQuery.filtered(Query.term("seqid", 1), or_filter, highlight=highlight)
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total >= 1, "Elastic filtered query retrieved marker(s)")

    def test_and_filtered_query(self):
        ''' Test building and running a filtered query. '''
        query_bool = BoolQuery(must_arr=[RangeQuery("start", gte=1)])
        and_filter = AndFilter(query_bool)
        and_filter.extend(RangeQuery("start", gte=1)) \
                  .extend(Query.term("seqid", 1))
        query = ElasticQuery.filtered(Query.term("seqid", 1), and_filter)
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total >= 1, "Elastic filtered query retrieved marker(s)")

    def test_not_filtered_query(self):
        ''' Test building and running a filtered query. '''
        not_filter = NotFilter(RangeQuery("start", lte=10000))
        query = ElasticQuery.filtered(Query.term("seqid", 1), not_filter)
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total >= 1, "Elastic filtered query retrieved marker(s)")

    def test_term_filtered_query(self):
        ''' Test filtered query with a term filter. '''
        query = ElasticQuery.filtered(Query.term("seqid", 1), Filter(Query.term("id", "rs373328635")))
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total == 1, "Elastic filtered query retrieved marker")

    def test_terms_filtered_query(self):
        ''' Test filtered query with a terms filter. '''
        terms_filter = TermsFilter.get_terms_filter("id", ["rs2476601", "rs373328635"])
        query = ElasticQuery.filtered(Query.term("seqid", 1), terms_filter)
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.search().hits_total >= 1, "Elastic filtered query retrieved marker(s)")

    def test_string_query(self):
        ''' Test building and running a string query. '''
        query = ElasticQuery.query_string("rs2476601", fields=["id"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        docs = elastic.search()
        self.assertTrue(len(docs.docs) == 1, "Elastic string query retrieved marker (rs2476601)")

    def test_string_query_with_wildcard(self):
        query = ElasticQuery.query_string("rs*", fields=["id"])
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'), size=5)
        result = elastic.search()
        self.assertTrue(result.hits_total > 1, "Elastic string query retrieved marker (rs*)")

    def test_match_query(self):
        ''' Test building and running a match query. '''
        query = ElasticQuery.query_match("id", "rs2476601")
        search = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(len(search.search().docs) == 1, "Elastic string query retrieved marker (rs2476601)")

    def test_term_query(self):
        ''' Test building and running a match query. '''
        query = ElasticQuery(Query.term("id", "rs2476601"))
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(len(elastic.search().docs) == 1, "Elastic string query retrieved marker (rs2476601)")

        query = ElasticQuery(Query.term("seqid", "1", boost=3.0))
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(len(elastic.search().docs) > 1, "Elastic string query retrieved markers  on chr1")

    def test_terms_query(self):
        ''' Test building and running a match query. '''
        highlight = Highlight(["id"])
        query = ElasticQuery(Query.terms("id", ["rs2476601", "rs373328635"]), highlight=highlight)
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        docs = elastic.search().docs
        self.assertTrue(len(docs) == 2,
                        "Elastic string query retrieved markers (rs2476601, rs373328635)")
        self.assertTrue(getattr(docs[0], 'seqid'), "Hit attribute found")
        self.assertTrue(docs[0].highlight() is not None, "highlighting found")

    def test_bool_query(self):
        ''' Test a bool query. '''
        query_bool = BoolQuery()
        highlight = Highlight(["id", "seqid"])
        query_bool.must(Query.term("id", "rs373328635")) \
                  .must(RangeQuery("start", gt=1000)) \
                  .must_not(Query.match("seqid", "2")) \
                  .should(Query.match("seqid", "3")) \
                  .should(Query.match("seqid", "1"))
        query = ElasticQuery.bool(query_bool, highlight=highlight)
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(len(elastic.search().docs) == 1, "Elastic string query retrieved marker (rs373328635)")

    def test_string_query_with_wildcard_and_highlight(self):
        highlight = Highlight("id", pre_tags="<strong>", post_tags="</strong>")
        query = ElasticQuery.query_string("rs*", fields=["id"], highlight=highlight)
        search = Search(query, idx=ElasticSettings.idx('DEFAULT'), size=5)
        self.assertTrue(len(search.search().docs) > 1, "Elastic string query retrieved marker (rs*)")

    def test_query_ids(self):
        ''' Test by query ids. '''
        query = ElasticQuery(Query.ids(['1', '2']))
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'), size=5)
        self.assertTrue(len(elastic.search().docs) == 2, "Elastic string query retrieved marker (rs*)")

    def test_count(self):
        ''' Test count the number of documents in an index. '''
        elastic = Search(idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_count()['count'] > 1, "Elastic count documents in an index")

    def test_count_with_query(self):
        ''' Test count the number of documents returned by a query. '''
        query = ElasticQuery(Query.term("id", "rs373328635"))
        elastic = Search(query, idx=ElasticSettings.idx('DEFAULT'))
        self.assertTrue(elastic.get_count()['count'] == 1, "Elastic count with a query")


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class AggregationsTest(TestCase):

    def test_query_error(self):
        self.assertRaises(AggregationError, Agg, "test", "termx", {"field": "seqid", "size": 0})
        self.assertRaises(AggregationError, Aggs, "test")

    def test_term(self):
        ''' Terms Aggregation '''
        agg_name = "test"
        agg = Agg(agg_name, "terms", {"field": "seqid", "size": 0})
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))
        r_aggs = search.search().aggs
        self.assertTrue(agg_name in r_aggs, "returned test aggregations")

        ''' Ids Query with Terms Aggregation'''
        query = ElasticQuery(Query.ids(['1', '2']))
        search = Search(search_query=query, aggs=aggs, idx=ElasticSettings.idx('DEFAULT'), size=5)
        r_aggs = search.search().aggs
        self.assertTrue(len(r_aggs[agg_name].get_buckets()) > 0, "returned test aggregation buckets")
        self.assertTrue(getattr(r_aggs[agg_name], 'buckets')[0]['doc_count'] >= 0, "bucket document count")

    def test_filter(self):
        ''' Filter Aggregation '''
        agg = [Agg('test_filter', 'filter', RangeQuery('start', gt='25000')),
               Agg('avg_start', 'avg', {"field": 'start'}),
               Agg('min_start', 'min', {"field": 'start'}),
               Agg('sum_start', 'sum', {"field": 'start'}),
               Agg('stats_start', 'stats', {"field": 'start'}),
               Agg('count_start', 'value_count', {"field": 'start'}),
               Agg('ext_stats_start', 'extended_stats', {"field": 'start'})]
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))

        r_aggs = search.search().aggs
        self.assertTrue('avg_start' in r_aggs, "returned avg aggregation")
        self.assertTrue('min_start' in r_aggs, "returned min aggregation")

        stats_keys = ["min", "max", "sum", "count", "avg"]
        self.assertTrue(all(hasattr(r_aggs['stats_start'], k)
                            for k in stats_keys),
                        "returned min aggregation")

        stats_keys.extend(["sum_of_squares", "variance", "std_deviation", "std_deviation_bounds"])
        self.assertTrue(all(hasattr(r_aggs['ext_stats_start'], k)
                            for k in stats_keys),
                        "returned min aggregation")

    def test_top_hits(self):
        ''' Top Hits Aggregation '''
        agg = [Agg('test_filter', 'filter', RangeQuery('start', gt='2000')),
               Agg('test_top_hits', 'top_hits', {"size": 1})]
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))
        hits = search.search().aggs['test_top_hits'].get_hits()
        self.assertTrue(len(hits) == 1, "returned the top hit")

    def test_filters(self):
        ''' Filters Aggregation '''
        filters = {'filters': {'start_gt': RangeQuery('start', gt='1000'),
                               'start_lt': RangeQuery('start', lt='100000')}}
        agg = Agg('test_filters', 'filters', filters)
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))
        r_aggs = search.search().aggs
        self.assertTrue('start_lt' in r_aggs['test_filters'].get_buckets(),
                        "returned avg aggregation")

    def test_missing(self):
        ''' Missing Aggregation '''
        agg = Agg("test_missing", "missing", {"field": "seqid"})
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))
        r_aggs = search.search().aggs
        self.assertTrue(getattr(r_aggs['test_missing'], 'doc_count') == 0,
                        "no missing seqid fields")

    def test_significant_terms(self):
        ''' Significant Terms Aggregation '''
        agg = Agg("test_significant_terms", "significant_terms", {"field": "start"})
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))
        r_aggs = search.search().aggs
        self.assertTrue('test_significant_terms' in r_aggs, "returned aggregations")

    def test_range(self):
        ''' Range Aggregation '''
        agg = Agg("test_range_agg", "range",
                  {"field": "start",
                   "ranges": [{"to": 10000},
                              {"from": 10000, "to": 15000}]})
        aggs = Aggs(agg)
        search = Search(aggs=aggs, idx=ElasticSettings.idx('DEFAULT'))
        r_aggs = search.search().aggs
        self.assertTrue(len(r_aggs['test_range_agg'].get_buckets()) == 2,
                        "returned two buckets in range aggregations")
