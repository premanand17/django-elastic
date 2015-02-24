from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from es.management.loaders.Marker import MarkerManager
from es.management.loaders.Genenames import GenenameManager

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to create an elasticsearch index and add data \n" \
           "./manage.py index_search --mapSNP --indexName [index name]\n" \
           "./manage.py index_search --indexName [index name] --indexSNP All.vcf\n" \
           "./manage.py index_search --mapGene --indexName [index name]\n" \
           "./manage.py index_search --indexName [index name] --indexGene " \
           "genenames.org.txt --org=human"

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
        make_option('--org',
                    dest='org',
                    help='Organism Name'),
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
        elif options['mapGene']:
            gene = GenenameManager()
            gene.create_genename_index(**options)
        elif options['indexGene']:
            gene = GenenameManager()
            gene.load_genename(**options)
        else:
            print(help)
