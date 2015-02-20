from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from es.management.loaders.Marker import MarkerManager

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to create an elasticsearch index and add data \n" \
           "python manage.py index_search --mapSNP --indexName dbSNP142\n" \
           "python manage.py index_search --indexName dbSNP142 --indexSNP " \
           "All.vcf"

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
        )

    def handle(self, *args, **options):
        if options['mapSNP']:
            marker = MarkerManager()
            marker.create_snp_index(**options)
        elif options['indexSNP']:
            marker = MarkerManager()
            marker.create_load_snp_index(**options)
        else:
            print(help)
