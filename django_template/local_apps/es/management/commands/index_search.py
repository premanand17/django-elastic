from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from es.management.loaders.Marker import MarkerManager

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to create an elasticsearch index and add data \n" \
           "python manage.py index_search --mapSNP --build dbSNP142\n" \
           "python manage.py index_search --build dbSNP142 --indexSNP All.vcf"

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
        make_option('--build',
                    dest='build',
                    help='Build number'),
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
