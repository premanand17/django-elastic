from elastic.management.loaders.loader import JSONLoader, MappingProperties
import requests
import json


class CriteriaManager(JSONLoader):

    def create_criteria(self, **options):
        ''' Create alias index mapping and load data '''
        idx_name = self.get_index_name(**options)
        idx_type = self.get_index_type(**options)
        print('idx name ' + idx_name)
        print('idx type ' + idx_type)
        mart_project = 'immunobase'
        mart_url = 'https://mart.' + mart_project + '.org/biomart/martservice?'
        mart_object = self.get_object_type(**options)
        mart_dataset = mart_project + '_criteria_' + mart_object
        criteria_json = self.get_criteria_info_from_biomart(mart_url, mart_dataset, **options)
        processed_criteria_json = self._post_process_criteria_info(criteria_json)
        #print(processed_criteria_json)
        self._create_criteria_mapping(**options)
        #self.load(criteria_json['data'], idx_name, idx_type)
        self.load(processed_criteria_json, idx_name, idx_type)

    def _create_criteria_mapping(self, **options):
        ''' Create the mapping for alias indexing '''
        idx_type = self.get_index_type(**options)
        # props = MappingProperties(idx_type)
        props = self.get_properties(**options)
        self.mapping(props.mapping_properties, idx_type=idx_type, meta=None, analyzer=self.KEYWORD_ANALYZER, **options)
        # mapping_json = {idx_type: props}
        # self.mapping(mapping_json, idx_type=idx_type, analyzer=self.KEYWORD_ANALYZER, **options)

    def _post_process_criteria_info(self, criteria_json):
        doc = []
        for row in criteria_json['data']:
            current_row = self.process_row(row)
            doc.append(current_row)
        return doc

    def process_row(self, row):
        current_row = {}
        current_row['Name'] = row['Name']
        current_row['Primary id'] = row['Primary id']
        current_row['Object class'] = row['Object class']
        current_row['Total score'] = row['Total score']
        for org in self.get_organism_enabled():
            for dis in self.get_diseases_enabled():
                dis_org_header = dis + '_' + org
                score_key = dis + ' ' + org + ' score'
                score_key = score_key.strip()

                flag_key = dis + ' ' + org + ' flag'
                flag_key = flag_key.strip()

                current_row_score = None
                current_row_flag = None

                if score_key in row:
                    current_row_score = row[score_key]

                if flag_key in row:
                    current_row_flag = row[flag_key]

                if current_row_score is None or len(current_row_score) == 0:
                    current_row_score = '0'

                if current_row_flag is None or len(current_row_flag) == 0:
                    current_row_flag = '0'

                if current_row_score is not None and current_row_flag is not None:
                    current_row_score_flag = current_row_score + ':' + current_row_flag
                    current_row[dis_org_header] = current_row_score_flag

        return current_row

    def get_properties(self, **options):
        ''' Create the mapping for criteria index '''
        idx_type = self.get_index_type(**options)
        props = MappingProperties(idx_type)
        props.add_property("Name", "string", analyzer="full_name")
        props.add_property("Primary id", "string", index="not_analyzed")
        props.add_property("Total score", "string", index="no")
        dis_orgs = self.get_dis_orgs()
        for dis_org in dis_orgs:
            props.add_property(dis_org, "string", index="no")

        return props

    def get_organism_enabled(self):
        # hard code for now, later fetch it from db
        org = ['Hs']
        # org = ['Hs', 'Mm', 'Rn']
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

    def get_object_type(self, **options):
        idx_type = self.get_index_type(**options)
        if(idx_type == 'gene'):
            return 'genes'
        if(idx_type == 'locus'):
            return 'regions'
        if(idx_type == 'marker'):
            return 'markers'
        if(idx_type == 'study'):
            return 'studies'

    def get_index_type(self, **options):
        ''' Get indexName option '''
        if options['indexType']:
            return options['indexType'].lower()
        return self.__class__.__name__ + '_type'

    def get_project(self, **options):
        ''' Get indexName option '''
        if options['project']:
            return options['project'].lower()
        return 'immunobase'

    def get_criteria_info_from_biomart(self, mart_url, mart_dataset, **options):
        urlTemplate = \
            mart_url + \
            'query=<?xml version="1.0" encoding="UTF-8"?>' \
            '<!DOCTYPE Query><Query client="pythonclient" processor="JSON" limit="-1" header="1">' \
            '<Dataset name="' + mart_dataset + '" config="criteria_config">' \
            '<Attribute name="criteria__object__main__primary_id"/>' \
            '<Attribute name="criteria__object__main__name"/>' \
            '<Attribute name="criteria__object__main__total_score"/>' \
            '<Attribute name="criteria__object__main__object_class"/>' \

        flag_query = ''
        for dis_org in self.get_dis_orgs():
            flag_query += '<Attribute name="criteria__object__main__' + dis_org + '"/>'
            flag_query += '<Attribute name="criteria__object__main__' + dis_org + '_flag"/>'

        urlTemplate += flag_query + '</Dataset>' + '</Query>'
        queryURL = urlTemplate
        req = requests.get(queryURL, stream=True)
        return req.json()
