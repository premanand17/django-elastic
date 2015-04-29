from elastic.management.loaders.loader import DelimeterLoader, MappingProperties


class MarkerManager(DelimeterLoader):

    def create_load_snp_index(self, **options):
        ''' Index VCF dbSNP data '''
        idx_name = self.get_index_name(**options)
        map_props = self._create_snp_mapping(**options)
        f = self.open_file_to_load('indexSNP', **options)
        self.load(map_props.get_column_names(), f, idx_name, 'marker', chunk=20000)

    def _create_snp_mapping(self, **options):
        ''' Create the mapping for snp index '''
        props = MappingProperties('marker')
        props.add_property("seqid", "string", index="not_analyzed")
        props.add_property("start", "integer", index="not_analyzed")
        props.add_property("id", "string", index="not_analyzed")
        props.add_property("ref", "string", index="no")
        props.add_property("alt", "string", index="no")
        props.add_property("qual", "string", index="no")
        props.add_property("filter", "string", index="no")
        props.add_property("info", "string", index="no")
        self.mapping(props, 'marker', **options)
        return props


class RsMerge(DelimeterLoader):

    def create_load_snp_merge_index(self, **options):
        ''' Index rs number merge dbSNP data '''
        idx_name = self.get_index_name(**options)
        map_props = self._create_rs_merge_mapping(**options)
        f = self.open_file_to_load('indexSNPMerge', **options)
        self.load(map_props.get_column_names(), f, idx_name, 'rs_merge', chunk=10000)

    def _create_rs_merge_mapping(self, **options):
        ''' Create the mapping for rs index '''
        props = MappingProperties('rs_merge')
        props.add_property("rshigh", "string", index="not_analyzed")
        props.add_property("rslow", "string", index="not_analyzed")
        props.add_property("build_id", "integer", index="no")
        props.add_property("orien", "integer", index="no")
        props.add_property("create_time", "date", index="no", property_format="yyyy-MM-dd HH:mm:ss.SSS")
        props.add_property("last_updated_time", "date", index="no", property_format="yyyy-MM-dd HH:mm:ss.SSS")
        props.add_property("rscurrent", "string", index="not_analyzed")
        props.add_property("orien2current", "string", index="no")
        props.add_property("notes", "string", index="no")
        self.mapping(props, 'rs_merge', **options)
        return props

    def parse_line(self, parts, column_names, idx_name, idx_type, is_GFF, is_GTF):
        ''' Overrides Delimeter.parse_line() - to prefix rs numbers with "rs". '''
        doc_data = {}
        for idx, p in enumerate(parts):
            p = p.strip()
            if column_names[idx] in ["rscurrent", "rslow", "rshigh"]:
                p = "rs"+p
            if self.is_str(column_names[idx], idx_name, idx_type):
                doc_data[column_names[idx]] = p
            elif p.isdigit():
                doc_data[column_names[idx]] = int(p)
            else:
                doc_data[column_names[idx]] = p
        return doc_data
