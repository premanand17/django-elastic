from search.management.loaders.Loader import DelimeterLoader


class GeneTargetManager(DelimeterLoader):

    def create_load_gene_target_index(self, **options):
        ''' Index gene target data '''
        idx_name = self.get_index_name(**options)
        self._create_gene_mapping(**options)
        f = self.open_file_to_load('indexGTarget', **options)
        column_names = ["ensg", "name", "biotype", "strand",
                        "baitChr", "baitStart", "baitEnd", "baitID", "baitName",
                        "oeChr", "oeStart", "oeEnd", "oeID", "oeName", "dist",
                        "Monocyte", "Macrophage", "Erythroblast", "Megakaryocyte",
                        "CD4_Naive", "CD4_Non_Activated", "CD4_Total", "CD4_Activated"]
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
                  "Monocyte": {"type": "float"},
                  "Macrophage": {"type": "float"},
                  "Erythroblast": {"type": "float"},
                  "Megakaryocyte": {"type": "float"},
                  "CD4_Naive": {"type": "float"},
                  "CD4_Non_Activated": {"type": "float"},
                  "CD4_Total": {"type": "float"},
                  "CD4_Activated": {"type": "float"}
                  }
                 }
        meta = {"Monocyte": "tissue_type",
                "Macrophage": "tissue_type",
                "Erythroblast": "tissue_type",
                "Megakaryocyte": "tissue_type",
                "CD4_Naive": "tissue_type",
                "CD4_Non_Activated": "tissue_type",
                "CD4_Total": "tissue_type",
                "CD4_Activated": "tissue_type"
                }
        meta = {"tissue_type": meta}
        props["_meta"] = meta
        mapping_json = {"gene_target": props}
        self.mapping(mapping_json, meta=meta, idx_type='gene_target', **options)
