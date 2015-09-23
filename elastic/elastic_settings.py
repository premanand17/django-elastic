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
        ''' Given the index name and optionally a type get the index URL path.
        If 'DEFAULT' is requested but not defined return the random index. '''
        idxs = cls.getattr('IDX', cluster=cluster)
        if idxs is None:
            logger.warn('No indexes defined')
            return
        if name in idxs:
            if isinstance(idxs[name], dict):
                idx = idxs[name]['name']
                if idx_type is not None:
                    if idx_type in idxs[name]['idx_type']:
                        if isinstance(idxs[name]['idx_type'][idx_type], dict):
                            return idx+'/'+idxs[name]['idx_type'][idx_type]['type']
                        else:
                            return idx+'/'+idxs[name]['idx_type'][idx_type]
                    else:
                        raise SettingsError('Index type key ('+idx_type+') not found.')
                else:
                    return idx
            return idxs[name]
        else:
            if name == 'DEFAULT':
                name = list(idxs.keys())[0]
                return ElasticSettings.idx(name=name, idx_type=idx_type, cluster=cluster)
        return None

    @classmethod
    def url(cls, cluster='default'):
        ''' Return the Elastic URL '''
        return cls.getattr('ELASTIC_URL', cluster=cluster)

    @classmethod
    def search_props(cls, idx_name='ALL', user=None):
        ''' Build the search index names, keys, types and suggesters. Return as a dictionary. '''
        eattrs = ElasticSettings.attrs()

        search_idx = set()
        search_types = set()
        for (key, value) in eattrs.get('IDX').items():
            if idx_name == 'ALL' or key == idx_name:
                if 'idx_type' in value:
                    for _type_key, type_values in value['idx_type'].items():
                        if 'search' in type_values:
                            search_idx.add(key)
                            search_types.add(type_values['type'])

        suggesters = eattrs.get('AUTOSUGGEST')

        idx_properties = {
                "idx": ','.join(ElasticSettings.idx(name) for name in search_idx),
                "idx_keys": list(search_idx),
                "idx_type": ','.join(itype for itype in search_types),
                "suggesters": ','.join(ElasticSettings.idx(name) for name in suggesters)
        }

        if 'pydgin_auth' in settings.INSTALLED_APPS:
            return cls.search_props_restricted(idx_properties, user)
        else:
            return idx_properties

    @classmethod
    def search_props_restricted(cls, idx_props, user=None):
        ''' Get a comma separated list of indices '''
        if 'pydgin_auth' in settings.INSTALLED_APPS:
            from pydgin_auth.permissions import check_index_perms
            from pydgin_auth.elastic_model_factory import ElasticPermissionModelFactory

            idx_keys, idx_types = ElasticPermissionModelFactory.get_elastic_model_names(as_list=True)
            idx_names_auth, idx_type_auth = check_index_perms(user, idx_keys, idx_types)

            idx_names_auth = [idx_name.replace(
                ElasticPermissionModelFactory.PERMISSION_MODEL_SUFFIX, '').upper() for idx_name in idx_names_auth]
            idx_names_auth = [name for name in idx_names_auth if name in idx_props['idx_keys']]
            idx = ','.join(ElasticSettings.idx(name) for name in idx_names_auth)

            idx_types_auth_tmp1 = [idx_type.replace(
                ElasticPermissionModelFactory.PERMISSION_MODEL_TYPE_SUFFIX, '') for idx_type in idx_type_auth]
            idx_types_auth_tmp2 = [idx_type.split(
                ElasticPermissionModelFactory.PERMISSION_MODEL_NAME_TYPE_DELIMITER)[1]
                for idx_type in idx_types_auth_tmp1]
            idx_types_auth = ','.join(t for t in idx_types_auth_tmp2 if t in idx_props['idx_type'])

            idx_props['idx'] = idx
            idx_props['idx_keys'] = idx_names_auth
            idx_props['idx_type'] = idx_types_auth
            return idx_props
        else:
            return idx_props

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
