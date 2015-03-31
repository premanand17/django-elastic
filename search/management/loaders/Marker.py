from search.management.loaders.Loader import DelimeterLoader


class MarkerManager(DelimeterLoader):

    def create_load_snp_index(self, **options):
        ''' Index VCF dbSNP data '''
        idx_name = self.get_index_name(**options)
        self._create_snp_mapping(**options)
        f = self.open_file_to_load('indexSNP', **options)
        column_names = ["seqid", "start", "id", "ref", "alt", "qual", "filter", "info"]
        self.load(column_names, f, idx_name, 'marker')

    def _create_snp_mapping(self, **options):
        ''' Create the mapping for snp index '''
        props = {"properties":
                 {"id": {"type": "string", "index": "not_analyzed"},
                  "seqid": {"type": "string", "index": "not_analyzed"},
                  "ref": {"type": "string", "index": "no"},
                  "alt": {"type": "string", "index": "no"},
                  "qual": {"type": "string", "index": "no"},
                  "filter": {"type": "string", "index": "no"},
                  "start": {"type": "integer", "index": "not_analyzed"},
                  "info": {"type": "string", "index": "no"}
                  }
                 }
        mapping_json = {"mappings": {"marker": props}}
        self.mapping(mapping_json, **options)
