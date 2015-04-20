from elastic.management.loaders.loader import DelimeterLoader, MappingProperties


class MarkerManager(DelimeterLoader):

    def create_load_snp_index(self, **options):
        ''' Index VCF dbSNP data '''
        idx_name = self.get_index_name(**options)
        self._create_snp_mapping(**options)
        f = self.open_file_to_load('indexSNP', **options)
        column_names = ["seqid", "start", "id", "ref", "alt", "qual", "filter", "info"]
        self.load(column_names, f, idx_name, 'marker', chunk=20000)

    def _create_snp_mapping(self, **options):
        ''' Create the mapping for snp index '''
        props = MappingProperties('marker')
        props.add_property("id", "string", index="not_analyzed")
        props.add_property("seqid", "string", index="not_analyzed")
        props.add_property("ref", "string", index="no")
        props.add_property("alt", "string", index="no")
        props.add_property("qual", "string", index="no")
        props.add_property("filter", "string", index="no")
        props.add_property("start", "integer", index="not_analyzed")
        props.add_property("info", "string", index="no")

        self.mapping(props, 'marker', **options)
