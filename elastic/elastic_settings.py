from django.conf import settings


class ElasticSettings:
    ''' Manage settings for the Elastic elastic app '''

    @classmethod
    def attrs(cls, cluster='default'):
        ''' Return list of attributes for a elastic cluster '''
        return getattr(settings, 'ELASTIC').get(cluster, None)

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
    def idx_only(cls, name='DEFAULT'):
        ''' Get the index only without the type. '''
        idx = cls.idx(name)
        if idx is not None:
            return cls._remove_type(idx)
        return idx

    @classmethod
    def url(cls, cluster='default'):
        ''' Return the Elastic URL '''
        return cls.getattr('ELASTIC_URL', cluster=cluster)

    @classmethod
    def indices_str(cls, cluster='default'):
        ''' Get a comma separated list of indices '''
        attrs = cls.attrs(cluster).get('IDX')
        s = set([cls._remove_type(v) for v in attrs.values()])
        return ','.join(str(e) for e in s)

    @classmethod
    def _remove_type(cls, idx):
        ''' If mapping type included then remove '''
        pos = idx.find('/')
        if pos > 0:
            idx = idx[:-(len(idx)-pos)]
        return idx
