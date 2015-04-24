from django.core.management.base import BaseCommand
from elastic.management.snapshot import Snapshot
from elastic.elastic_settings import ElasticSettings


class Command(BaseCommand):
    help = "Show available snapshot(s)."

    def add_arguments(self, parser):
        parser.add_argument('--snapshot',
                            dest='snapshot',
                            default='_all',
                            help='Snapshot name')
        parser.add_argument('--repo',
                            dest='repo',
                            default=ElasticSettings.getattr('REPOSITORY'),
                            metavar=ElasticSettings.getattr('REPOSITORY'),
                            help='Repository name')
        parser.add_argument('--all',
                            dest='all',
                            action='store_true',
                            help='List all repositories')

    def handle(self, *args, **options):
        Snapshot.show(options['repo'], options['snapshot'], options['all'])
