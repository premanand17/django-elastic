from elastic.management.loaders.loader import DelimeterLoader


class GFFManager(DelimeterLoader):

    def create_load_gff_index(self, **options):
        ''' Index gff data '''
        self._create_gff_mapping(**options)
        idx_name = self.get_index_name(**options)
        idx_type = self._get_index_type(**options)
        f = self.open_file_to_load('indexGFF', **options)
        column_names = ["seqid", "source", "type", "start", "end", "score", "strand", "phase", "attr"]
        self.load(column_names, f, idx_name, idx_type, is_GFF=True, is_GTF=options['isGTF'])

    def _create_gff_mapping(self, **options):
        ''' Create the mapping for gff index '''
        index_type = self._get_index_type(**options)
        props = {"properties":
                 {"seqid": {"type": "string"},
                  "source": {"type": "string"},
                  "type": {"type": "string", "index": "not_analyzed"},
                  "start": {"type": "integer", "index": "not_analyzed"},
                  "end": {"type": "integer", "index": "not_analyzed"},
                  "score": {"type": "string", "index": "no"},
                  "strand": {"type": "string", "index": "no"},
                  "phase": {"type": "string", "index": "no"},
                  "attr": {"type": "object"}
                  }
                 }
        mapping_json = {index_type: props}
        self.mapping(mapping_json, index_type, **options)

    def _get_index_type(self, **options):
        if options['indexType']:
            return options['indexType'].lower()
        return "gff"
