import re
import requests
import json
from search.management.loaders.loader import Loader
from search.elastic_model import ElasticSettings
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
            resp = requests.put(ElasticSettings.url()+'/' +
                                index_name+'/disease/'+parts[2],
                                data=json.dumps(data))
            if resp.status_code == 201:
                logger.debug("Loaded "+parts[0])
            else:
                logger.error("Problem loading "+parts[0])

    def _create_disease_mapping(self, **options):
        ''' Create the mapping for disease indexing '''
        props = {"properties":
                 {"name": {"type": "string", "boost": 4, "index": "not_analyzed"},
                  "code": {"type": "string", "index": "not_analyzed"},
                  "description": {"type": "string", "index": "not_analyzed"},
                  "colour": {"type": "string", "index": "not_analyzed"},
                  "tier": {"type": "integer", "index": "not_analyzed"},
                  }
                 }
        mapping_json = {"disease": props}
        self.mapping(mapping_json, 'disease', **options)
