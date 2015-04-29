from elastic.management.loaders.loader import DelimeterLoader, MappingProperties


class GFFManager(DelimeterLoader):

    def create_load_gff_index(self, **options):
        ''' Index gff data '''
        mapping_props = self._create_gff_mapping(**options)
        idx_name = self.get_index_name(**options)
        idx_type = self._get_index_type(**options)
        f = self.open_file_to_load('indexGFF', **options)
        column_names = mapping_props.get_column_names()
        self.load(column_names, f, idx_name, idx_type, is_GFF=True, is_GTF=options['isGTF'])

    def _create_gff_mapping(self, **options):
        ''' Create the mapping for gff index '''
        idx_type = self._get_index_type(**options)
        props = MappingProperties(idx_type)
        props.add_property("seqid", "string", index="not_analyzed") \
             .add_property("source", "string") \
             .add_property("type", "string", index="not_analyzed") \
             .add_property("start", "integer", index="not_analyzed") \
             .add_property("end", "integer", index="not_analyzed") \
             .add_property("score", "string", index="no") \
             .add_property("strand", "string", index="no") \
             .add_property("phase", "string", index="no") \
             .add_property("attr", "object")
        self.mapping(props, idx_type, **options)
        return props

    def _get_index_type(self, **options):
        if options['indexType']:
            return options['indexType'].lower()
        return "gff"
