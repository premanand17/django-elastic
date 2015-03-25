from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from search.management.loaders.Marker import MarkerManager
from search.management.loaders.Region import RegionManager
from search.management.loaders.Gene import GeneManager
from search.management.loaders.Disease import DiseaseManager
from search.management.loaders.GeneTarget import GeneTargetManager
from search.management.loaders.GFF import GFFManager


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    ''' Elastic index mapping and loading tool. '''
    help = "Use to create Elastic index mappings and load data.\n\n" \
           "Usage: ./manage.py index_search [options]\n" \
           "Options for regions:\n" \
           " --mapRegion --build GRCh38\n" \
           " --indexRegion region.gff --build GRCh38 --disease t1d|ms|cro|all (default: all) --regionType assoc\n" \
           "Options for markers:\n" \
           " --indexName [index name] --indexSNP All.vcf\n" \
           "Options for genes:\n" \
           " --indexName [index name] --indexGene genenames.org.txt --org=human\n" \
           " --indexName [index name] --indexGeneGFF gene.gff --build GRCh38\n" \
           "Options for diseases:\n" \
           " --indexName [index name] --indexDisease disease.list\n" \
           "Options for GFF/GTF:\n" \
           " --indexName [index name] --indexType [gff] --indexGFF file.gff [--isGTF]"

    option_list = BaseCommand.option_list + (
        make_option('--indexSNP',
                    dest='indexSNP',
                    help='VCF file (from dbSNP) to index'),
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
        make_option('--indexDisease',
                    dest='indexDisease',
                    help='Load disease details'),
        ) + (
        make_option('--indexGTarget',
                    dest='indexGTarget',
                    help='Load gene targets'),
        ) + (
        make_option('--indexGFF',
                    dest='indexGFF',
                    help='Load GFF targets'),
        ) + (
        make_option('--isGTF',
                    dest='isGTF',
                    help='GTF file type',
                    action="store_true"),
        ) + (
        make_option('--indexType',
                    dest='indexType',
                    help='Index type'),
        )

    def handle(self, *args, **options):
        ''' Handle the user options to map or load data. '''
        if options['indexSNP']:
            marker = MarkerManager()
            marker.create_load_snp_index(**options)

        elif options['mapRegion']:
            region = RegionManager()
            region.create_region_index(**options)
        elif options['indexRegion']:
            region = RegionManager()
            region.create_load_region_index(**options)

        elif options['indexGene']:
            gene = GeneManager()
            gene.load_genename(**options)
        elif options['indexGeneGFF']:
            gene = GeneManager()
            gene.update_gene(**options)

        elif options['indexDisease']:
            disease = DiseaseManager()
            disease.create_disease(**options)

        elif options['indexGTarget']:
            gt = GeneTargetManager()
            gt.create_load_gene_target_index(**options)

        elif options['indexGFF']:
            gff = GFFManager()
            gff.create_load_gff_index(**options)
        else:
            print(help)
