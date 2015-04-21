from django.core.management.base import BaseCommand, CommandError
from elastic.management.snapshot import Snapshot


class Command(BaseCommand):
    help = "Create or delete a repository. For example: " \
           "./manage.py repository REPOSITORY --dir /path_to_repository/" \
           "./manage.py repository REPOSITORY --delete"

    def add_arguments(self, parser):
        parser.add_argument('repo',
                            type=str,
                            help='Repository name.')
        parser.add_argument('--dir',
                            dest='dir',
                            help='Directory to store repository.')
        parser.add_argument('--delete',
                            dest='delete',
                            action='store_true',
                            help='Delete repository.')

    def handle(self, *args, **options):
        if options['delete']:
            Snapshot.delete_repository(options['repo'])
        else:
            if not options['dir']:
                raise CommandError("the following arguments are required: dir")
            Snapshot.create_repository(options['repo'], options['dir'])
