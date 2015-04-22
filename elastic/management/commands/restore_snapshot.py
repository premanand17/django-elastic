from django.core.management.base import BaseCommand
from elastic.management.snapshot import Snapshot
from elastic.elastic_settings import ElasticSettings


class Command(BaseCommand):
    help = "Restore a snapshot. For example: " \
           "./manage.py restore_snapshot SNAPSHOT [--url Elastic URL, e.g http://localhost:9200]"
    help += " [--repo " + ElasticSettings.getattr('REPOSITORY') + "]"

    def add_arguments(self, parser):
        parser.add_argument('snapshot',
                            type=str,
                            help='Snapshot to restore.')
        parser.add_argument('--url',
                            dest='url',
                            default=ElasticSettings.url(),
                            help='Elastic URL to restore to.')
        parser.add_argument('--repo',
                            dest='repo',
                            default=ElasticSettings.getattr('REPOSITORY'),
                            help='Repository name')

    def handle(self, *args, **options):
        Snapshot.restore_snapshot(options['repo'], options['snapshot'], options['url'])
