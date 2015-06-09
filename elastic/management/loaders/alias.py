from elastic.management.loaders.loader import DelimeterLoader, MappingProperties
import re
from os.path import os


class AliasManager(DelimeterLoader):

    def create_alias(self, **options):
        ''' Create alias index mapping and load data '''
        idx_name = None
        root_dir = None
        idx_feature_type = None

        if options['indexName']:
            idx_name = options['indexName'].lower()
        if(options['indexAlias']):
            root_dir = options['indexAlias']
        if(options['indexFeatureType']):
            idx_feature_type = options['indexFeatureType']

        object_types = ['gene', 'locus', 'marker', 'study']
        for object_ in object_types:
            idx_dir = object_ + '_alias'

            if idx_name is None:
                idx_name_cur = object_ + '_alias_test'
            else:
                idx_name_cur = idx_name

            if idx_feature_type is not None:
                if object_ != idx_feature_type:
                    print(object_ + '!=' + idx_feature_type + ' Going to continue....')
                    continue

            print('root dir ' + root_dir + '  index name: ' + idx_name_cur)
            idx_file = None
            types = self.get_index_types(object_)
            for type_ in types:
                print(idx_name_cur + ' <===> ' + type_)
                if root_dir.endswith('/'):
                    idx_file = root_dir + idx_dir + '/' + type_ + '.tsv'
                else:
                    idx_file = root_dir + '/' + idx_dir + '/' + type_ + '.tsv'
                print ('idx_file ' + idx_file)

                if (os.path.exists(root_dir) and os.path.exists(idx_file)):
                    print(idx_file + ' Exists === Proceeding to index')
                    print(' Idx Name ' + idx_name_cur + ' idx type ' + type_)
                    options['indexAlias'] = idx_file
                    options['indexType'] = type_
                    options['indexName'] = idx_name_cur
                    self._create_alias_mapping(type_, **options)
                    f = self.open_file_to_load('indexAlias', **options)
                    column_names = ["internal_id", "alias", "preferred_name", "type"]
                    self.load(column_names, f, idx_name_cur, type_)
                    print('======================Index created for ' + type_ + ' with index name ' + idx_name_cur)
                else:
                    print(idx_file + ' Does not Exists ===. Please check if file exists.... Proceeding to quit')

    def _create_alias_mapping(self, idx_alias_type, **options):
        ''' Create the mapping for alias indexing '''
        props = MappingProperties(idx_alias_type)
        props.add_property("internal_id", "string", index="not_analyzed")
        props.add_property("alias", "string", analyzer="full_name", index_options="offsets")
        props.add_property("preferred_name", "string", analyzer="full_name")
        props.add_property("type", "string", analyzer="standard")
        print(props.mapping_properties)
        self.mapping(props, idx_type=idx_alias_type, meta=None, analyzer=self.KEYWORD_ANALYZER,
                     **options)

    def get_index_alias_type(self, **options):
        ''' Get indexName option '''
        if options['indexType']:
            return options['indexType'].lower()
        else:
            return self.__class__.__name__ + '_type'

    def get_index_types(self, object_type):
        index_types = []
        if(re.search(r'gene', object_type)):
                index_types.extend(["human", "mouse", "rat"])
        elif(re.search(r'marker', object_type)):
                index_types.extend(["rs", "ic", "dil", "position", "extra"])
        elif(re.search(r'locus', object_type)):
                index_types.extend(self.get_diseases_enabled())
        elif(re.search(r'study', object_type)):
                index_types.extend(["ImmunoBase", "T1DBase"])
        return index_types

    def get_diseases_enabled(self):
        disease = ['AS', 'ATD', 'CEL', 'CRO', 'JIA', 'MS', 'PBC', 'PSO', 'RA', 'SLE', 'T1D', 'UC', 'AA', 'IBD', 'NAR', 'PSC', 'SJO', 'SSC', 'VIT']
        return sorted(disease)
