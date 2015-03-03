from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from es.management.loaders.Marker import MarkerManager
from es.management.loaders.Region import RegionManager
from es.management.loaders.Gene import GeneManager
from es.management.loaders.Disease import DiseaseManager


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    ''' Elasticsearch index mapping and loading tool. '''
    help = "Use to create elasticsearch index mappings and load data.\n\n" \
           "Usage: ./manage.py index_search [options]\n" \
           "Options for regions:\n" \
           " --mapRegion --build GRCh38\n" \
           " --indexRegion region.gff --build GRCh38 --disease t1d|ms|cro|all (default: all) --regionType assoc\n" \
           "Options for markers:\n" \
           " --indexName [index name] --mapSNP\n" \
           " --indexName [index name] --indexSNP All.vcf\n" \
           "Options for genes:\n" \
           " --indexName [index name] --mapGene\n" \
           " --indexName [index name] --indexGene genenames.org.txt --org=human\n" \
           " --indexName [index name] --indexGeneGFF gene.gff --build GRCh38\n" \
           "Options for diseases:\n" \
           " --indexName [index name] --mapDisease\n" \
           " --indexName [index name] --indexDisease disease.list"

    option_list = BaseCommand.option_list + (
        make_option('--mapSNP',
                    dest='mapSNP',
                    action="store_true",
                    help='Create a marker index mapping'),
        ) + (
        make_option('--indexSNP',
                    dest='indexSNP',
                    help='VCF file (from dbSNP) to index'),
        ) + (
        make_option('--mapGene',
                    dest='mapGene',
                    action="store_true",
                    help='Create gene mapping'),
        ) + (
        make_option('--indexGene',
                    dest='indexGene',
                    help='Genename.org file to index'),
        ) + (
        make_option('--indexGeneGFF',
                    dest='indexGeneGFF',
                    help='GFF gene file used to update a gene index'),
        ) + (
        make_option('--org',
                    dest='org',
                    help='Organism name'),
        ) + (
        make_option('--indexName',
                    dest='indexName',
                    help='Index name'),
        ) + (
        make_option('--mapRegion',
                    dest='mapRegion',
                    action="store_true",
                    help='Create a region index mapping'),
        ) + (
        make_option('--indexRegion',
                    dest='indexRegion',
                    help='GFF file to index (e.g. celiac_regions.gff'),
        ) + (
        make_option('--regionType',
                    dest='regionType',
                    help='region type (eg: assoc, ortho, linkage, qtl'),
        ) + (
        make_option('--build',
                    dest='build',
                    help='Build name (e.g. GRCh38)'),
        ) + (
        make_option('--disease',
                    dest='disease',
                    help='disease code (eg: cel) '),
        ) + (
        make_option('--mapDisease',
                    dest='mapDisease',
                    action="store_true",
                    help='Create a disease index mapping'),
        ) + (
        make_option('--indexDisease',
                    dest='indexDisease',
                    help='Load disease details'),
        )

    def handle(self, *args, **options):
        ''' Handle the user options to map or load data. '''
        if options['mapSNP']:
            marker = MarkerManager()
            marker.create_snp_index(**options)
        elif options['indexSNP']:
            marker = MarkerManager()
            marker.create_load_snp_index(**options)

        elif options['mapRegion']:
            region = RegionManager()
            region.create_region_index(**options)
        elif options['indexRegion']:
            region = RegionManager()
            region.create_load_region_index(**options)

        elif options['mapGene']:
            gene = GeneManager()
            gene.create_genename_index(**options)
        elif options['indexGene']:
            gene = GeneManager()
            gene.load_genename(**options)
        elif options['indexGeneGFF']:
            gene = GeneManager()
            gene.update_gene(**options)

        elif options['mapDisease']:
            disease = DiseaseManager()
            disease.create_disease_index(**options)
        elif options['indexDisease']:
            disease = DiseaseManager()
            disease.create_disease(**options)
        else:
            print(help)
