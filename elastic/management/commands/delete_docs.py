''' Delete the Elastic index documents. '''
import logging
from optparse import make_option
from django.core.management.base import BaseCommand
from elastic.search import Delete
import sys


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
            idx_type = ''
            if options['indexType']:
                idx_type = options['indexType']

            sys.stdout.write("WARNING: About to delete index "+options['indexName']+'/'+idx_type+'. Continue [y/n]?')
            choice = input().lower()
            if choice == 'y':
                Delete.docs_by_query(options['indexName'], idx_type=idx_type)
        else:
            print(Command.help)
