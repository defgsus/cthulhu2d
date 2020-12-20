
from ..es.exporter import EsExporterBase


class EsPoolExporter(EsExporterBase):

    INDEX_NAME = "game-evo-pool"

    MAPPINGS = {
        "properties": {
            "timestamp": {"type": "date"},
            "pool_id": {"type": "keyword"},
            "phenotype_id": {"type": "keyword"},
            "generation": {"type": "long"},
            "num_phenotypes": {"type": "integer"},
            "phenotype": {"type": "keyword"},
            "name": {"type": "keyword"},
        }
    }
