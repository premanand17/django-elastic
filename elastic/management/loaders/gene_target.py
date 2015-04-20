from elastic.management.loaders.loader import DelimeterLoader


class GeneTargetManager(DelimeterLoader):

    def create_load_gene_target_index(self, **options):
        ''' Index gene target data '''
        idx_name = self.get_index_name(**options)
        self._create_gene_mapping(**options)
        f = self.open_file_to_load('indexGTarget', **options)
        column_names = ["ensg", "name", "biotype", "strand",
                        "baitChr", "baitStart", "baitEnd", "baitID", "baitName",
                        "oeChr", "oeStart", "oeEnd", "oeID", "oeName", "dist",
                        "Monocytes", "Macrophages_M0", "Macrophages_M1", "Macrophages_M2", "Neutrophils",
                        "Megakaryocytes", "Endothelial_precursors", "Erythroblasts", "Foetal_thymus", "Naive_CD4",
                        "Total_CD4_MF", "Total_CD4_Activated", "Total_CD4_NonActivated", "Naive_CD8", "Total_CD8",
                        "Naive_B", "Total_B"]

        self.load(column_names, f, idx_name, 'gene_target')

    def _create_gene_mapping(self, **options):
        ''' Create the mapping for gene target index '''
        props = {"properties":
                 {"ensg": {"type": "string", "index": "not_analyzed", "boost": 4},
                  "name": {"type": "string", "index": "not_analyzed"},
                  "biotype": {"type": "string", "index": "not_analyzed"},
                  "strand": {"type": "string", "index": "no"},
                  "baitChr": {"type": "string", "index": "no"},
                  "baitStart": {"type": "integer", "index": "not_analyzed"},
                  "baitEnd": {"type": "integer", "index": "not_analyzed"},
                  "baitID": {"type": "string", "index": "no"},
                  "baitName": {"type": "string", "index": "no"},
                  "oeChr": {"type": "string", "index": "no"},
                  "oeStart": {"type": "integer", "index": "not_analyzed"},
                  "oeEnd": {"type": "integer", "index": "not_analyzed"},
                  "oeID": {"type": "string", "index": "no"},
                  "oeName": {"type": "string", "index": "no"},
                  "dist": {"type": "integer", "index": "not_analyzed"},
                  "Monocytes": {"type": "float"},
                  "Macrophages_M0": {"type": "float"},
                  "Macrophages_M1": {"type": "float"},
                  "Macrophages_M2": {"type": "float"},
                  "Neutrophils": {"type": "float"},
                  "Megakaryocytes": {"type": "float"},
                  "Endothelial_precursors": {"type": "float"},
                  "Erythroblasts": {"type": "float"},
                  "Foetal_thymus": {"type": "float"},
                  "Naive_CD4": {"type": "float"},
                  "Total_CD4_MF": {"type": "float"},
                  "Total_CD4_Activated": {"type": "float"},
                  "Total_CD4_NonActivated": {"type": "float"},
                  "Naive_CD8": {"type": "float"},
                  "Total_CD8": {"type": "float"},
                  "Naive_B": {"type": "float"},
                  "Total_B": {"type": "float"}
                  }
                 }
        meta = {"Monocytes": "tissue_type",
                "Macrophages_M0": "tissue_type",
                "Macrophages_M1": "tissue_type",
                "Macrophages_M2": "tissue_type",
                "Neutrophils": "tissue_type",
                "Megakaryocytes": "tissue_type",
                "Endothelial_precursors": "tissue_type",
                "Erythroblasts": "tissue_type",
                "Foetal_thymus": "tissue_type",
                "Naive_CD4": "tissue_type",
                "Total_CD4_MF": "tissue_type",
                "Total_CD4_Activated": "tissue_type",
                "Total_CD4_NonActivated": "tissue_type",
                "Naive_CD8": "tissue_type",
                "Total_CD8": "tissue_type",
                "Naive_B": "tissue_type",
                "Total_B": "tissue_type"
                }
        meta = {"tissue_type": meta}
        # props["_meta"] = meta
        mapping_json = {"gene_target": props}
        self.mapping(mapping_json, idx_type='gene_target', meta=meta, **options)
