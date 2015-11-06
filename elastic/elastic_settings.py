''' Used to manage and retrieve Elastic settings. '''
from django.conf import settings
from elastic.exceptions import SettingsError
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


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
    def idx(cls, name='DEFAULT', idx_type=None, cluster='default'):
        ''' Given the index key and optionally a type get the index URL path.
        If 'DEFAULT' is requested but not defined return a random index. '''
        (idx, idx_type) = cls.idx_names(idx_key=name, idx_type=idx_type, cluster=cluster)
        if idx is not None:
            if idx_type is None:
                return idx
            else:
                return idx + '/' + idx_type
        return None

    @classmethod
    def idx_names(cls, idx_key='DEFAULT', idx_type=None, cluster='default'):
        ''' Given the index key and optionally type key return a tuple of
        their names. If 'DEFAULT' is requested but not defined in the settings
        return a random index. '''
        idxs = cls.getattr('IDX', cluster=cluster)
        if idxs is None:
            logger.warn('No indexes defined')
            return (None, None)
        if idx_key in idxs:
            if isinstance(idxs[idx_key], dict):
                idx = idxs[idx_key]['name']
                if idx_type is not None:
                    if idx_type in idxs[idx_key]['idx_type']:
                        if isinstance(idxs[idx_key]['idx_type'][idx_type], dict):
                            return (idx, idxs[idx_key]['idx_type'][idx_type]['type'])
                        else:
                            return (idx, idxs[idx_key]['idx_type'][idx_type])
                    else:
                        raise SettingsError('Index type key ('+idx_type+') not found.')
                else:
                    return (idx, None)
            return (idxs[idx_key], None)
        else:
            if idx_key == 'DEFAULT':
                idx_key = list(idxs.keys())[0]
                return ElasticSettings.idx_names(idx_key=idx_key, idx_type=idx_type, cluster=cluster)
        return (None, None)

    @classmethod
    def url(cls, cluster='default'):
        ''' Return the Elastic URL '''
        return ElasticUrl.get_url(cluster='default')

    @classmethod
    def get_idx_types(cls, idx_name='DEFAULT', cluster='default', user=None):
        idxs = cls.getattr('IDX', cluster=cluster)
        if idxs is None:
            return None
        if idx_name in idxs:
            return idxs[idx_name]['idx_type']

    @classmethod
    def search_props(cls, idx_name='ALL', user=None):
        ''' Build the search index names, keys, types and suggesters. Return as a dictionary. '''
        eattrs = ElasticSettings.attrs()
        search_idx = set()
        search_types = set()
        suggester_idx = []
        for (idx_key, idx_values) in eattrs.get('IDX').items():
            if idx_name == 'ALL' or idx_key == idx_name:
                if 'idx_type' in idx_values:
                    for type_key, type_values in idx_values['idx_type'].items():
                        if 'search' in type_values:
                            search_idx.add(idx_key)
                            search_types.add(idx_key+'.'+type_key)
                if 'suggester' in idx_values:
                    suggester_idx.append(idx_key)

        if 'pydgin_auth' in settings.INSTALLED_APPS:
            from pydgin_auth.permissions import get_authenticated_idx_and_idx_types
            search_idx, search_types = get_authenticated_idx_and_idx_types(user, search_idx, search_types)
            suggester_idx = get_authenticated_idx_and_idx_types(user, idx_keys=suggester_idx, idx_type_keys=[])[0]

        idx_properties = {
            "idx": ','.join(ElasticSettings.idx(name) for name in search_idx),
            "idx_keys": list(search_idx),
            "idx_type": ','.join(ElasticSettings.idx_names(ty.split('.', 1)[0], idx_type=ty.split('.', 1)[1])[1]
                                 for ty in search_types),
            "suggester_keys": suggester_idx
        }
        return idx_properties

    @classmethod
    def indices_str(cls, cluster='default'):
        ''' Get a comma separated list of indices '''
        attrs = cls.attrs(cluster).get('IDX')
        s = set()
        for v in attrs.values():
            if isinstance(v, dict):
                s.add(v['name'])
            else:
                s.add(v)
        return ','.join(str(e) for e in s)

    @classmethod
    def get_idx_key_by_name(cls, val):
        ''' Get the index key from the name in the dictionary.
        @type  val: value
        @param val: A value in the dictionary.
        '''
        for k, v in ElasticSettings.attrs().get('IDX').items():
            if isinstance(v, str) and v == val:
                return k
            elif isinstance(v, dict) and v['name'] == val:
                return k

    @classmethod
    def get_label(cls, idx, idx_type=None, label='label'):
        ''' Get an index or index type label. '''
        try:
            if idx_type is not None:
                return ElasticSettings.attrs().get('IDX')[idx]['idx_type'][idx_type][label]
            return ElasticSettings.attrs().get('IDX')[idx][label]
        except KeyError:
            raise SettingsError(label+' not found in '+idx)


class ElasticUrl(object):
    ''' Manage elastic urls settings. '''
    URL_INDEX = 0

    @classmethod
    def get_url(cls, cluster='default'):
        urls = ElasticSettings.getattr('ELASTIC_URL', cluster=cluster)
        if isinstance(urls, str):
            return urls
        try:
            return urls[ElasticUrl.URL_INDEX]
        except IndexError:
            ElasticUrl.URL_INDEX = 0
            return urls[ElasticUrl.URL_INDEX]

    @classmethod
    def rotate_url(cls, cluster='default'):
        ''' Rotate the host used in an array of elastic urls. '''
        urls = ElasticSettings.getattr('ELASTIC_URL', cluster=cluster)
        if isinstance(urls, str):
            logger.warn("Just one elastic url (ELASTIC_URL) defined.")
            return

        logger.debug("Rotate old HOST_INDEX = "+str(ElasticUrl.URL_INDEX))
        if len(urls) <= (ElasticUrl.URL_INDEX+1):
            ElasticUrl.URL_INDEX = 0
        else:
            ElasticUrl.URL_INDEX += 1
        logger.debug("Rotate new HOST_INDEX = "+str(ElasticUrl.URL_INDEX))
