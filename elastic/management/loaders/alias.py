from elastic.management.loaders.loader import DelimeterLoader, MappingProperties
import re
from os.path import os


class AliasManager(DelimeterLoader):

    def create_alias(self, **options):
        ''' Create alias index mapping and load data '''
        idx_name = self.get_index_name(**options)
        idx_alias_type = self.get_index_alias_type(**options)

        if(options['indexName']) == 'locus_alias':
            root_dir = options['indexAlias']
            print('root dir ' + root_dir + '  index name: ' + idx_name)
            for dis in self.get_diseases_enabled():
                idx_alias_type = dis
                options['indexType'] = idx_alias_type
                if root_dir.endswith('/'):
                    dis_file = root_dir + dis + '.tsv'
                else:
                    dis_file = root_dir + '/' + dis + '.tsv'

                if (os.path.exists(root_dir) and os.path.exists(dis_file)):
                    print(dis_file + ' Exists ')
                    options['indexAlias'] = dis_file
                    self._create_alias_mapping(idx_alias_type, **options)
                    f = self.open_file_to_load('indexAlias', **options)
                    column_names = ["internal_id", "alias", "preferred_name", "type"]
                    self.load(column_names, f, idx_name, idx_alias_type)
                    print('Index created for ' + idx_alias_type + ' with index name ' + idx_name)
                else:
                    print(dis_file + ' Do NOT Exists ')

        else:
            self._create_alias_mapping(idx_alias_type, **options)
            file_name = options['indexAlias']
            print('File name ' + file_name + '  index name: ' + idx_name)
            f = self.open_file_to_load('indexAlias', **options)
            column_names = ["internal_id", "alias", "preferred_name", "type"]
            self.load(column_names, f, idx_name, idx_alias_type)

    def _create_alias_mapping(self, idx_alias_type, **options):
        ''' Create the mapping for alias indexing '''
        props = MappingProperties(idx_alias_type)
        props.add_property("internal_id", "string", index="not_analyzed")
        props.add_property("alias", "string", analyzer="full_name")
        props.add_property("preferred_name", "string", analyzer="full_name")
        props.add_property("type", "string", analyzer="standard")
        print(props.mapping_properties)
        self.mapping(props.mapping_properties, idx_type=idx_alias_type, meta=None, analyzer=self.KEYWORD_ANALYZER,
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
            if(len(self.get_organism_enabled()) > 1):
                index_types.extend(["human", "mouse", "rat"])
            else:
                index_types.extend(["human"])
        elif(re.search(r'marker', object_type)):
                index_types.extend(["rs", "ic"])
        elif(re.search(r'locus', object_type)):
                index_types.extend(self.get_diseases_enabled())
        elif(re.search(r'study', object_type)):
                index_types.extend(["study"])

    def get_organism_enabled(self):
        org = ['Hs']
        return sorted(org)

    def get_diseases_enabled(self):
        disease = ['AS', 'ATD', 'CEL', 'CRO', 'JIA', 'MS', 'PBC', 'PSO', 'RA', 'SLE', 'T1D', 'UC', 'OD']
        # disease = ['T1D']
        return sorted(disease)

    def get_dis_orgs(self):
        dis_orgs = []
        orgs_enabled = self.get_organism_enabled()
        dis_enabled = self.get_diseases_enabled()
        for dis in dis_enabled:
            for org in orgs_enabled:
                dis_orgs.append(dis + '_' + org)
        # dis_orgs = ['AS_Hs', 'ATD_Hs', 'CEL_Hs', 'CRO_Hs', 'JIA_Hs', 'MS_Hs', 'PBC_Hs', 'PSO_Hs', 'RA_Hs', 'SLE_Hs',
        #            'T1D_Hs', 'UC_Hs', 'OD_Hs']
        return sorted(dis_orgs)
