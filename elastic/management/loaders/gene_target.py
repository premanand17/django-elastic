''' Loader for gene target data. '''
import re

from elastic.management.loaders.loader import DelimeterLoader
from elastic.management.loaders.mapping import MappingProperties


class GeneTargetManager(DelimeterLoader):
    tissue_types = []

    column_names = ["ensg", "name", "biotype", "strand",
                    "baitChr", "baitStart", "baitEnd", "baitID", "baitName",
                    "oeChr", "oeStart", "oeEnd", "oeID", "oeName", "dist"]

    def create_load_gene_target_index(self, **options):
        ''' Index gene target data '''
        idx_name = self.get_index_name(**options)
        idx_type = self.get_index_type('gene_target', **options)
        f = self.open_file_to_load('indexGTarget', **options)
        line = f.readline()
        line = line.decode("utf-8")
        cols = re.split('\t', line)
        for i in range(len(GeneTargetManager.column_names), len(cols)-1):
            GeneTargetManager.tissue_types.append(cols[i])

        self._create_gene_mapping(idx_type, **options)
        GeneTargetManager.column_names.extend(GeneTargetManager.tissue_types)
        self.load(GeneTargetManager.column_names, f, idx_name, idx_type, chunk=20000)

    def _create_gene_mapping(self, idx_type, **options):
        ''' Create the mapping for gene target index '''
        props = MappingProperties("gene_target")
        props.add_property("ensg", "string", index="not_analyzed") \
             .add_property("name", "string", index="not_analyzed") \
             .add_property("biotype", "string", index="not_analyzed") \
             .add_property("strand", "string", index="no") \
             .add_property("baitChr", "string", index="not_analyzed") \
             .add_property("baitStart", "integer", index="not_analyzed") \
             .add_property("baitEnd", "integer", index="not_analyzed") \
             .add_property("baitID", "string", index="no") \
             .add_property("baitName", "string", index="no") \
             .add_property("oeChr", "string", index="not_analyzed") \
             .add_property("oeStart", "integer", index="not_analyzed") \
             .add_property("oeEnd", "integer", index="not_analyzed") \
             .add_property("oeID", "string", index="no") \
             .add_property("oeName", "string", index="no") \
             .add_property("dist", "integer", index="not_analyzed")

        meta = {"tissue_type": {}}
        for tt in GeneTargetManager.tissue_types:
            props.add_property(tt, "float")
            meta["tissue_type"][tt] = "tissue_type"

        self.mapping(props, idx_type, meta=meta, **options)
