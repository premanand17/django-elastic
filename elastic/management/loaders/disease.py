''' Loader for disease data. '''
import re
import requests
import json
from elastic.management.loaders.loader import Loader
from elastic.management.loaders.mapping import MappingProperties
from elastic.search import ElasticSettings
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DiseaseManager(Loader):

    def create_disease(self, **options):
        ''' Create disease index mapping and load data '''
        index_name = self.get_index_name(**options)
        self._create_disease_mapping(**options)

        f = self.open_file_to_load('indexDisease', **options)
        for line in f:
            line = line.strip().decode("utf-8")
            if line.startswith("#"):
                continue
            parts = re.split('\t', line)
            data = {"name": parts[0],
                    "code": parts[2],
                    "description": parts[1],
                    "colour": parts[3],
                    "tier": int(parts[4])
                    }
            data['suggest'] = {}
            data['suggest']["input"] = [parts[2], parts[0]]
            data['suggest']["weight"] = 250
            resp = requests.put(ElasticSettings.url()+'/' +
                                index_name+'/disease/'+parts[2],
                                data=json.dumps(data))
            if resp.status_code == 201:
                logger.debug("Loaded "+parts[0])
            else:
                logger.error("Problem loading "+parts[0])

    def _create_disease_mapping(self, **options):
        ''' Create the mapping for disease indexing '''
        props = MappingProperties("disease")
        props.add_property("name", "string") \
             .add_property("code", "string") \
             .add_property("description", "string", index="not_analyzed") \
             .add_property("colour", "string", index="not_analyzed") \
             .add_property("tier", "integer", index="not_analyzed") \
             .add_property("suggest", "completion", analyzer="full_name")

        tags = MappingProperties("tags")
        tags.add_property("weight", "integer", index="not_analyzed")
        props.add_properties(tags)
        self.mapping(props, 'disease', analyzer=Loader.KEYWORD_ANALYZER, **options)
