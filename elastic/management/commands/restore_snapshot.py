from django.core.management.base import BaseCommand
from elastic.management.snapshot import Snapshot
from elastic.elastic_settings import ElasticSettings


class Command(BaseCommand):
    help = "Restore a snapshot."

    def add_arguments(self, parser):
        parser.add_argument('snapshot',
                            type=str,
                            help='Snapshot to restore.')
        parser.add_argument('--url',
                            dest='url',
                            default=ElasticSettings.url(),
                            metavar="ELASTIC_URL",
                            help='Elastic URL to restore to.')
        parser.add_argument('--repo',
                            dest='repo',
                            default=ElasticSettings.getattr('REPOSITORY'),
                            metavar=ElasticSettings.getattr('REPOSITORY'),
                            help='Repository name')
        parser.add_argument('--indices',
                            dest='indices',
                            default=None,
                            metavar="idx1,idx2",
                            help='Indices (comma separated) to be restored from a snapshot (default all).')

    def handle(self, *args, **options):
        Snapshot.restore_snapshot(options['repo'], options['snapshot'], options['url'], options['indices'])
