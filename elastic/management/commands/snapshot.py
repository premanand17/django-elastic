from django.core.management.base import BaseCommand
from elastic.management.snapshot import Snapshot
from elastic.elastic_settings import ElasticSettings


class Command(BaseCommand):
    help = "Create or delete a snapshot. For example: " \
           "./manage.py snapshot SNAPSHOT [--indices idx1,idx2]"
    help += " [--repo " + ElasticSettings.getattr('REPOSITORY') + "]"
    help += " [--delete]"

    def add_arguments(self, parser):
        parser.add_argument('snapshot',
                            type=str,
                            help='New snapshot name.')
        parser.add_argument('--indices',
                            dest='indices',
                            default=None,
                            help='Indices (comma separated) to create a snapshot for.')
        parser.add_argument('--repo',
                            dest='repo',
                            default=ElasticSettings.getattr('REPOSITORY'),
                            help='Repository name')
        parser.add_argument('--delete',
                            dest='delete',
                            action='store_true',
                            help='Delete snapshot.')

    def handle(self, *args, **options):
        if options['delete']:
            Snapshot.delete_snapshot(options['repo'], options['snapshot'])
        else:
            Snapshot.create_snapshot(options['repo'], options['snapshot'], options['indices'])
