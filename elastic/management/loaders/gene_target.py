from elastic.management.loaders.loader import DelimeterLoader, MappingProperties


class GeneTargetManager(DelimeterLoader):
    tissue_types = ["Monocytes", "Macrophages_M0", "Macrophages_M1", "Macrophages_M2", "Neutrophils",
                    "Megakaryocytes", "Endothelial_precursors", "Erythroblasts", "Foetal_thymus", "Naive_CD4",
                    "Total_CD4_MF", "Total_CD4_Activated", "Total_CD4_NonActivated", "Naive_CD8", "Total_CD8",
                    "Naive_B", "Total_B"]

    def create_load_gene_target_index(self, **options):
        ''' Index gene target data '''
        idx_name = self.get_index_name(**options)
        self._create_gene_mapping(**options)
        f = self.open_file_to_load('indexGTarget', **options)
        column_names = ["ensg", "name", "biotype", "strand",
                        "baitChr", "baitStart", "baitEnd", "baitID", "baitName",
                        "oeChr", "oeStart", "oeEnd", "oeID", "oeName", "dist"]
        column_names.extend(GeneTargetManager.tissue_types)

        self.load(column_names, f, idx_name, 'gene_target')

    def _create_gene_mapping(self, **options):
        ''' Create the mapping for gene target index '''
        props = MappingProperties("gene_target")
        props.add_property("ensg", "string", index="not_analyzed")
        props.add_property("name", "string", index="not_analyzed")
        props.add_property("biotype", "string", index="not_analyzed")
        props.add_property("strand", "string", index="no")
        props.add_property("baitChr", "string", index="no")
        props.add_property("baitStart", "integer", index="not_analyzed")
        props.add_property("baitEnd", "integer", index="not_analyzed")
        props.add_property("baitID", "string", index="no")
        props.add_property("baitName", "string", index="no")
        props.add_property("oeChr", "string", index="no")
        props.add_property("oeStart", "integer", index="not_analyzed")
        props.add_property("oeEnd", "integer", index="not_analyzed")
        props.add_property("oeID", "string", index="no")
        props.add_property("oeName", "string", index="no")
        props.add_property("dist", "integer", index="not_analyzed")

        meta = {"tissue_type": {}}
        for tt in GeneTargetManager.tissue_types:
            props.add_property(tt, "float")
            meta["tissue_type"][tt] = "tissue_type"

        self.mapping(props, idx_type='gene_target', meta=meta, **options)
