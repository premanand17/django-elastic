''' Utility functions. '''
from elastic.query import Query, ScoreFunction, FunctionScoreQuery, BoolQuery,\
    RangeQuery, OrFilter
from elastic.search import ElasticQuery, Search
import random


class ElasticUtils(object):
    ''' Utility functions. '''

    @classmethod
    def get_docs_count(cls, idx, idx_type, search_query=None):
        '''Get index or search doc counts'''
        return Search(idx=idx, idx_type=idx_type, search_query=search_query, size=0).get_count()['count']

    @classmethod
    def get_rdm_feature_id(cls, idx, idx_type, qbool=Query.match_all(), sources=[], field=None):
        ''' Get a random feature id from the indices. '''
        doc = cls.get_rdm_docs(idx, idx_type, qbool=qbool, sources=sources, size=1)[0]
        if field is not None:
            return getattr(doc, field)
        return doc.doc_id()

    @classmethod
    def get_rdm_docs(cls, idx, idx_type, qbool=Query.match_all(), sources=[], size=1):
        ''' Get a random doc from the indices. '''
        score_function1 = ScoreFunction.create_score_function('random_score', seed=random.randint(0, 1000000))

        search_query = ElasticQuery(FunctionScoreQuery(qbool, [score_function1], boost_mode='replace'),
                                    sources=sources)
        elastic = Search(search_query=search_query, size=size, idx=idx, idx_type=idx_type)
        try:
            return elastic.search().docs
        except IndexError:
            return cls.get_rdm_docs(idx, idx_type, qbool, sources, size)

    @classmethod
    def get_rdm_feature_ids(cls, idx, idx_type, qbool=Query.match_all(), sources=[], field=None, size=1):
        ''' Get random feature_ids from the indices. '''
        docs = cls.get_rdm_docs(idx, idx_type, qbool=qbool, sources=sources, size=size)
        ids = []
        for doc in docs:
            if field is not None:
                ids.append(getattr(doc, field))
            else:
                ids.append(doc.doc_id())
        return ids

    @classmethod
    def range_overlap_query(cls, seqid, start_range, end_range,
                            field_list=None, seqid_param="seqid", start_param="start", end_param="end"):
        ''' Constructs a range overlap query '''
        query_bool = BoolQuery(must_arr=[RangeQuery(start_param, lte=start_range),
                                         RangeQuery(end_param, gte=end_range)])
        or_filter = OrFilter(RangeQuery(start_param, gte=start_range, lte=end_range))
        or_filter.extend(RangeQuery(end_param, gte=start_range, lte=end_range)) \
                 .extend(query_bool)
        return ElasticQuery.filtered(Query.term(seqid_param, seqid), or_filter, field_list)
