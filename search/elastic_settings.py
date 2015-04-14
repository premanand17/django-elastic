from django.conf import settings


class ElasticSettings:
    ''' Manage settings for the Elastic search app '''

    @classmethod
    def attrs(cls, cluster='default'):
        ''' Return list of attributes for a search cluster '''
        return getattr(settings, 'SEARCH').get(cluster, None)

    @classmethod
    def getattr(cls, name, cluster='default'):
        ''' Get a named attribute '''
        return cls.attrs(cluster).get(name, None)

    @classmethod
    def default_idx(cls):
        ''' Get the default index '''
        return cls.getattr('DEFAULT_IDX')

    @classmethod
    def url(cls, cluster='default'):
        ''' Return the Elastic URL '''
        return cls.getattr('ELASTIC_URL', cluster=cluster)

    @classmethod
    def indices_str(cls, cluster='default'):
        ''' Get a comma separated list of indices (assumes names contain _IDX) '''
        attrs = cls.attrs()
        s = set([v for (k, v) in attrs.items() if '_IDX' in k])
        return ','.join(str(e) for e in s)
