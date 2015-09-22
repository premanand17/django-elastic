''' Update the Elastic index documents in bulk using the scan & schroll and Update APIs '''
from django.core.management.base import BaseCommand
from optparse import make_option
import logging
from elastic.management.loaders.update import UpdateManager


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    ''' Elastic index updating tool. '''
    help = "Use to update Elastic index\n\n" \
           "Options:\n" \
           " --indexName [index name] --indexType [index type] --json_data [file with json data to add] " \

    option_list = BaseCommand.option_list + (
        make_option('--update',
                    dest='update',
                    help='update elastic index',
                    action="store_true"),
        ) + (
        make_option('--random_update',
                    dest='random_update',
                    help='update elastic index random documents',
                    action="store_true"),
        ) + (
        make_option('--indexName',
                    dest='indexName',
                    help='Index name'),
        ) + (
        make_option('--indexType',
                    dest='indexType',
                    help='Index type'),
        ) + (
        make_option('--json_data',
                    dest='json_data',
                    help='JSON data'),
        )

    def handle(self, *args, **options):
        ''' Handle the user options to update elastic docs. '''
        if options['update']:
            logger.debug('indexName : ' + str(options['indexName']))
            logger.debug('indexType : ' + str(options['indexType']))
            logger.debug('json_data: ' + str(options['json_data']))

            updatemgr = UpdateManager()
            updatemgr.update_idx(**options)
        else:
            print(help)
