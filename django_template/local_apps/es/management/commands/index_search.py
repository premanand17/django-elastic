from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from es.management.loaders.Marker import MarkerManager
from es.management.loaders.Region import RegionManager

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to create an elasticsearch index and add data \n" \
           "python manage.py index_search --mapSNP --indexName dbSNP142\n" \
           "python manage.py index_search --indexName dbSNP142 --indexSNP All.vcf\n"\
           "python manage.py index_search --mapRegion --org_build GRCh38 --disease t1d|ms|cro|all (default: all)\n" \
           "python manage.py index_search --indexRegion region.gff --org_build GRCh38 --disease t1d|ms|cro|all (default: all)\n"


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
                    help='GFF file to index'),
        ) + (
        make_option('--org_build',
                    dest='org_build',
                    help='Organism BuildName'),
        ) + (
        make_option('--disease',
                    dest='disease',
                    help='disease code'),
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
        else:
            print(help)
