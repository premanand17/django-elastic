''' Elastic L{Result}, hit L{Document} and L{Aggregation} objects. '''


class Result(object):
    ''' Result container for Document and Aggregation stores. '''

    def __init__(self, took=None, hits_total=None, size=None,
                 docs=None, aggs=None, idx=None, query=None):
        ''' Store Documents and Aggregations and search meta data.
        @type  took: integer
        @keyword took: Time in milliseconds for search to run.
        @type  hits_total: integer
        @keyword hits_total: Total number of docs matching search criteria.
        @type  size: integer
        @keyword size: maximum number of hits returned
        @type  docs: list
        @keyword docs: L{Document} hits.
        @type  aggs: dict
        @keyword aggs: L{Aggregation} results.
        @type  idx: string
        @keyword idx: Indices searched.
        @type  query: dict
        @keyword query: search query
        '''
        self.took = took
        self.hits_total = hits_total
        self.size = size
        self.docs = docs
        self.aggs = aggs
        self.idx = idx
        self.query = query


class Document(object):
    ''' Generic object to hold Elastic document. Enables the use
    of getattr() on the document to get named attributes. '''
    def __init__(self, doc=None):
        if '_source' in doc:
            src = doc['_source']
            if hasattr(src, 'items'):
                self.__dict__.update(src)

        self.__dict__['_meta'] = {}
        if hasattr(doc, 'items'):
            for item in doc:
                if item != '_source':
                    self.__dict__['_meta'].update({item: doc[item]})

    def __getattr__(self, name):
        ''' Return Document attribute. '''
        return self.get(name, None)

    def __setattr__(self, name, value):
        ''' Set a Document attribute. '''
        self.__dict__[name] = value

    def to_dict(self):
        return self

    def type(self):
        ''' Document type. '''
        if '_type' in self.__dict__['_meta']:
            return self.__dict__['_meta']['_type']
        return None

    def highlight(self):
        ''' Highlight match. '''
        if 'highlight' in self.__dict__['_meta']:
            return self.__dict__['_meta']['highlight']
        return None


class Aggregation(object):
    ''' Generic object to hold Elastic aggregation. '''

    def __init__(self, agg=None):
        if hasattr(agg, 'items'):
            self.__dict__.update(agg)

    def __getattr__(self, name):
        ''' Return Aggregation attribute. '''
        return self.get(name, None)

    def __setattr__(self, name, value):
        ''' Set a Aggregation attribute. '''
        self.__dict__[name] = value

    def get_buckets(self):
        ''' Return Aggregation buckets. '''
        return self.__dict__['buckets']

    def get_hits(self):
        ''' Return Aggregation hits. '''
        return self.__dict__['hits']['hits']

    @classmethod
    def build_aggs(cls, json_response):
        ''' Utility for creating the set of Aggregation instances from
        an Elastic search result. '''
        aggs = None
        if 'aggregations' in json_response:
            aggs_list = json_response['aggregations']
            for agg_name in aggs_list:
                if aggs is None:
                    aggs = {}
                aggs[agg_name] = Aggregation(aggs_list[agg_name])
        return aggs
