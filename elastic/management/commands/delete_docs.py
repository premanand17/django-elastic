''' Delete the Elastic index documents. '''
import logging
from optparse import make_option
from django.core.management.base import BaseCommand
from elastic.search import Delete


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    ''' Elastic index document deleting tool. '''
    help = "Use to delete documents from an index\n\n" \
           "Options:\n" \
           " --indexName [index name] --indexType [index type] " \

    option_list = BaseCommand.option_list + (
        make_option('--indexName',
                    dest='indexName',
                    help='Index name'),
        ) + (
        make_option('--indexType',
                    dest='indexType',
                    help='Index type'),
        )

    def handle(self, *args, **options):
        ''' Handle the user options to update elastic docs. '''
        if options['indexName']:
            logger.debug('indexName : ' + str(options['indexName']))
            idx_type = ''
            if options['indexType']:
                logger.debug('indexType : ' + str(options['indexType']))
                idx_type = options['indexType']
            else:
                logger.debug('NO INDEX TYPE PROVIDED')
            Delete.docs_by_query(options['indexName'], idx_type=idx_type)
        else:
            print(Command.help)
