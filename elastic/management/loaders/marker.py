''' Loader for marker data (I{e.g.} VCF). '''
from elastic.management.loaders.loader import DelimeterLoader, Loader
from elastic.management.loaders.mapping import MappingProperties


class MarkerManager(DelimeterLoader):

    def create_load_snp_index(self, **options):
        ''' Index VCF dbSNP data '''
        idx_name = self.get_index_name(**options)
        idx_type = self.get_index_type('marker', **options)
        map_props = self._create_snp_mapping(idx_type, **options)
        f = self.open_file_to_load('indexSNP', **options)
        self.load(map_props.get_column_names()[:-1], f, idx_name, idx_type, chunk=20000)

    def _create_snp_mapping(self, idx_type, **options):
        ''' Create the mapping for snp index '''
        props = MappingProperties(idx_type)
        props.add_property("seqid", "string", index="not_analyzed") \
             .add_property("start", "integer", index="not_analyzed") \
             .add_property("id", "string", index="not_analyzed") \
             .add_property("ref", "string", index="no") \
             .add_property("alt", "string", index="no") \
             .add_property("qual", "string", index="no") \
             .add_property("filter", "string", index="no") \
             .add_property("info", "string", index="no") \
             .add_property("suggest", "completion",
                           index_analyzer="full_name", search_analyzer="full_name")
        tags = MappingProperties("tags")
        tags.add_property("weight", "integer", index="no")
        props.add_properties(tags)
        self.mapping(props, idx_type, analyzer=Loader.KEYWORD_ANALYZER, **options)
        return props


class RsMerge(DelimeterLoader):

    def create_load_snp_merge_index(self, **options):
        ''' Index rs number merge dbSNP data '''
        idx_name = self.get_index_name(**options)
        idx_type = self.get_index_type('rs_merge', **options)
        map_props = self._create_rs_merge_mapping(idx_type, **options)
        f = self.open_file_to_load('indexSNPMerge', **options)
        self.load(map_props.get_column_names(), f, idx_name, idx_type, chunk=10000)

    def _create_rs_merge_mapping(self, idx_type, **options):
        ''' Create the mapping for rs index '''
        props = MappingProperties(idx_type)
        props.add_property("rshigh", "string", index="not_analyzed") \
             .add_property("rslow", "string", index="not_analyzed") \
             .add_property("build_id", "integer", index="no") \
             .add_property("orien", "integer", index="no") \
             .add_property("create_time", "date", index="no", property_format="yyyy-MM-dd HH:mm:ss.SSS") \
             .add_property("last_updated_time", "date", index="no", property_format="yyyy-MM-dd HH:mm:ss.SSS") \
             .add_property("rscurrent", "string", index="not_analyzed") \
             .add_property("orien2current", "string", index="no") \
             .add_property("notes", "string", index="no")
        self.mapping(props, idx_type, **options)
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
