''' Old web-site criteria builder. '''
from elastic.management.loaders.loader import JSONLoader, MappingProperties
import requests
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CriteriaManager(JSONLoader):
    ''' Code to generate criteria index used in the old web-site. '''

    def create_criteria(self, **options):
        ''' Create alias index mapping and load data '''
        idx_name = self.get_index_name(**options)
        idx_types = self.get_index_type(**options)
        mart_project = self.get_project(**options)

        for idx_type in idx_types:
            logger.warn('idx name ' + idx_name)
            logger.warn('idx_type' + idx_type)
            logger.warn('project name ' + mart_project)
            mart_url = 'https://mart.' + mart_project + '.org/biomart/martservice?'
            # mart_url = 'https://mart-dev-imb/biomart/martservice?'
            mart_object = self.get_object_type(idx_type)
            logger.warn('mart_project ' + mart_project + '  mart_object ' + mart_object)
            mart_dataset = mart_project + '_criteria_' + mart_object
            criteria_json = self.get_criteria_info_from_biomart(mart_url, mart_dataset, idx_type, **options)
            processed_criteria_json = self._post_process_criteria_info(criteria_json, **options)
            self._create_criteria_mapping(**options)
            self.load(processed_criteria_json, idx_name, idx_type)

    def _create_criteria_mapping(self, **options):
        ''' Create the mapping for alias indexing '''
        idx_types = self.get_index_type(**options)

        for idx_type in idx_types:
            props = self.get_properties(idx_type, **options)
            self.mapping(props, idx_type=idx_type, meta=None, analyzer=self.KEYWORD_ANALYZER, **options)

    def _post_process_criteria_info(self, criteria_json, **options):
        doc = []
        for row in criteria_json['data']:
            current_row = self.process_row(row, **options)
            doc.append(current_row)
        return doc

    def process_row(self, row, **options):
        current_row = {}
        current_row['Name'] = row['Name']
        current_row['Primary id'] = row['Primary id']
        current_row['Object class'] = row['Object class']
        current_row['Total score'] = row['Total score']
        for org in self.get_organism_enabled(**options):
            for dis in self.get_diseases_enabled(**options):
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

    def get_properties(self, idx_type, **options):
        ''' Create the mapping for criteria index '''
        props = MappingProperties(idx_type)
        props.add_property("Name", "string", analyzer="full_name")
        props.add_property("Primary id", "string", index="not_analyzed")
        props.add_property("Total score", "string", index="no")
        dis_orgs = self.get_dis_orgs(**options)
        for dis_org in dis_orgs:
            props.add_property(dis_org, "string", index="no")

        return props

    def get_organism_enabled(self, **options):
        project = self.get_project(**options)
        if(project == "immunobase"):
            return ['Hs']
        elif(project == "t1dbase"):
            return ['Hs', 'Mm', 'Rn']

        return ['Hs']

    def get_diseases_enabled(self, **options):
        project = self.get_project(**options)
        if(project == "immunobase"):
            return sorted(['AS', 'ATD', 'CEL', 'CRO', 'JIA', 'MS', 'PBC', 'PSO', 'RA', 'SLE', 'T1D', 'UC', 'OD'])
        elif(project == "t1dbase"):
            return ['T1D']

        return sorted(['AS', 'ATD', 'CEL', 'CRO', 'JIA', 'MS', 'PBC', 'PSO', 'RA', 'SLE', 'T1D', 'UC', 'OD'])

    def get_dis_orgs(self, **options):
        dis_orgs = []
        orgs_enabled = self.get_organism_enabled(**options)
        dis_enabled = self.get_diseases_enabled(**options)
        for dis in dis_enabled:
            for org in orgs_enabled:
                dis_orgs.append(dis + '_' + org)
        return sorted(dis_orgs)

    def get_object_type(self, idx_type):
        ''' Get object type  '''
        if(idx_type == 'gene'):
            return 'genes'
        if(idx_type == 'locus'):
            return 'regions'
        if(idx_type == 'marker'):
            return 'markers'
        if(idx_type == 'study'):
            return 'studies'

    def get_index_type(self, **options):
        ''' Get indexType option '''
        idx_type = []
        if options['indexType']:
            idx_type.append(options['indexType'].lower())
        else:
            idx_type.extend(['gene', 'locus', 'marker', 'study'])
        return idx_type

    def get_project(self, **options):
        '''return project name'''
        if options['indexProject']:
            return options['indexProject'].lower()
        else:
            return "immunobase"

    def get_criteria_info_from_biomart(self, mart_url, mart_dataset, idx_type, **options):
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
        for dis_org in self.get_dis_orgs(**options):
            flag_query += '<Attribute name="criteria__object__main__' + dis_org + '"/>'
            flag_query += '<Attribute name="criteria__object__main__' + dis_org + '_flag"/>'

        urlTemplate += flag_query

        if(options['applyFilter']):
            filter_value = ''
            if(idx_type == 'gene'):
                filter_value = 'ptpn22'
            elif(idx_type == 'locus'):
                filter_value = '1p13.2'
            elif(idx_type == 'marker'):
                filter_value = 'rs2476601'
            elif(idx_type == 'study'):
                filter_value = 'barrett'

            filter_query = '<Filter name="criteria__alias__dm__alias" value="' + filter_value + '" filter_list=""/>'
            urlTemplate += filter_query

        urlTemplate += '</Dataset>' + '</Query>'
        queryURL = urlTemplate
        req = requests.get(queryURL, stream=True, verify=False)
        return req.json()
