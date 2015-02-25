from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from es.management.loaders.Marker import MarkerManager
from es.management.loaders.Region import RegionManager
from es.management.loaders.Gene import GeneManager


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to create an elasticsearch index and add data \n" \
           "./manage.py index_search --mapRegion --build GRCh38 --disease t1d|ms|cro|all (default: all)\n" \
           "./manage.py index_search --indexRegion region.gff --build GRCh38 --disease t1d|ms|cro|all (default: all)\n" \
           "./manage.py index_search --mapSNP --indexName [index name]\n" \
           "./manage.py index_search --indexName [index name] --indexSNP All.vcf\n" \
           "./manage.py index_search --mapGene --indexName [index name]\n" \
           "./manage.py index_search --indexName [index name] --indexGene " \
           "genenames.org.txt --org=human" \
           "./manage.py index_search --indexName [index name] --indexGeneGFF " \
           "gene.gff"

    option_list = BaseCommand.option_list + (
        make_option('--mapSNP',
                    dest='mapSNP',
                    action="store_true",
                    help='Create SNP index mapping'),
        ) + (
        make_option('--indexSNP',
                    dest='indexSNP',
                    help='VCF file to index'),
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
                    help='Genename.org file to index'),
        ) + (
        make_option('--org',
                    dest='org',
                    help='Organism Name'),
        ) + (
        make_option('--indexName',
                    dest='indexName',
                    help='Index Name'),
        ) + (
        make_option('--mapRegion',
                    dest='mapRegion',
                    action="store_true",
                    help='Create Region index mapping'),
        ) + (
        make_option('--indexRegion',
                    dest='indexRegion',
                    help='GFF file to index (eg: celiac_regions.gff'),
        ) + (
        make_option('--build',
                    dest='build',
                    help='BuildName (eg: GRCh38)'),
        ) + (
        make_option('--disease',
                    dest='disease',
                    help='disease code (eg: cel) '),
        )

    def handle(self, *args, **options):
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
            gene.load_gene_GFF(**options)
        else:
            print(help)
