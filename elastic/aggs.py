''' Define elastic aggregation(s) to be used in a search. '''
from elastic.query import Query
from elastic.exceptions import AggregationError


class Aggs:
    ''' Define a set of Aggregations. '''

    def __init__(self, agg_arr=None):
        self.aggs = {"aggregations": {}}
        if agg_arr is not None:
            if not isinstance(agg_arr, list):
                agg_arr = [agg_arr]
            for agg in agg_arr:
                if not isinstance(agg, Agg):
                    raise AggregationError('not an aggregation')
                self.aggs["aggregations"].update(agg.agg)


class Agg:
    ''' Aggregation Builder '''

    AGGS = {
        # metric aggregation
        "avg": {"type": dict, "params": {"field": str}},
        "min": {"type": dict, "params": {"field": str}},
        "max": {"type": dict, "params": {"field": str}},
        "sum": {"type": dict, "params": {"field": str}},
        "stats": {"type": dict, "params": {"field": str}},
        "extended_stats": {"type": dict, "params": {"field": str}},
        "value_count": {"type": dict, "params": {"field": str}},
        "top_hits": {"type": dict, "params": {"from": int, "size": int, "sort": list,
                                              "_source": list, "highlight": dict}},

        # bucket aggregation
        "global": {"type": dict},
        "filter": {"type": Query},
        "filters": {"type": dict, "dict_type": Query},
        "missing": {"type": dict, "params": {"field": str}},
        "terms": {"type": dict, "params": {"field": str, "size": int, "order": (dict, list)}},
        "significant_terms": {"type": dict, "params": {"field": str}},
        "range": {"type": dict, "params": {"field": str, 'ranges': list}}
    }

    def __init__(self, agg_name, agg_type, agg_body, sub_agg=None):
        ''' Construct an aggregation based on the aggregation type.

        @type  agg_name: str
        @param agg_name: Aggregation name.
        @type  agg_type: str
        @param agg_type: Aggregation type (from AGGS).
        @type  agg_body: dict
        @param agg_body: Aggregation body.
        @type  sub_agg: Agg
        @param sub_agg: Bucketing aggregations can have sub-aggregations.
        '''
        self.agg = {agg_name: {}}
        AGGS = Agg.AGGS

        if agg_type in AGGS:
            if isinstance(agg_body, AGGS[agg_type]["type"]):
                if 'params' in Agg.AGGS[agg_type]:
                    for pkey in agg_body:
                        if pkey not in Agg.AGGS[agg_type]['params']:
                            raise AggregationError(pkey+' unrecognised aggregation parameter')
                        if not isinstance(agg_body[pkey], Agg.AGGS[agg_type]['params'][pkey]):
                            raise AggregationError('aggregation parameter incorrect type')

                if 'list_type' in AGGS[agg_type]:
                    Agg._array_types(agg_body, AGGS[agg_type]['list_type'])
                    str_arr = []
                    [str_arr.append(Agg._get_query(q)) for q in agg_body]
                    self.agg[agg_name][agg_type] = str_arr
                elif 'dict_type' in AGGS[agg_type]:
                    self.agg[agg_name][agg_type] = self._update_dict(agg_body)
                else:
                    self.agg[agg_name][agg_type] = Agg._get_query(agg_body)
        else:
            raise AggregationError('aggregation type unknown: '+agg_type)

        if sub_agg is not None:
            self.agg[agg_name]['aggs'] = sub_agg.agg

    def _update_dict(self, qdict):
        for k, v in qdict.items():
            if isinstance(v, dict):
                qdict[k] = self._update_dict(v)
            else:
                qdict[k] = self._get_query(v)
        return qdict

    @classmethod
    def _get_query(cls, q):
        ''' Given a Query instance then return the Query dictionary. '''
        if hasattr(q, 'query'):
            return q.query
        return q

    @classmethod
    def _array_types(cls, arr, atype):
        ''' Evaluate if array contents are atype objects. '''
        if not all(isinstance(y, (atype)) for y in arr):
            raise AggregationError("not a "+str(atype))
        return True
