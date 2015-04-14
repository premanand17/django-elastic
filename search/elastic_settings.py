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
    def idx(cls, name='DEFAULT'):
        ''' Get the index. For the DEFAULT if not defined return the first index. '''
        idxs = cls.getattr('IDX')
        if name in idxs:
            return idxs[name]
        else:
            if name == 'DEFAULT':
                return idxs[list(idxs.keys())[0]]
            return None

    @classmethod
    def url(cls, cluster='default'):
        ''' Return the Elastic URL '''
        return cls.getattr('ELASTIC_URL', cluster=cluster)

    @classmethod
    def indices_str(cls, cluster='default'):
        ''' Get a comma separated list of indices (assumes names contain _IDX) '''
        attrs = cls.attrs(cluster).get('IDX')
        s = set([v for v in attrs.values()])
        return ','.join(str(e) for e in s)
