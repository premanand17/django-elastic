from django.test.runner import DiscoverRunner
from django.conf import settings
from django.db import connection

# http://www.caktusgroup.com/blog/2010/09/24/simplifying-the-testing-of-unmanaged-database-models-in-django/
class ManagedModelTestRunner(DiscoverRunner):
    """
    DiscoverRunner subclass that creates un-managed tables from a file containing
    the database schema (given by settings.TEST_DB_UNMANAGED_TABLES_SCHEMA_FILE)
    """
    def setup_databases(self, **kwargs):
        ret = super(ManagedModelTestRunner,self).setup_databases(**kwargs)
        cur = connection.cursor()
        schema_fn = settings.TEST_DB_UNMANAGED_TABLES_SCHEMA_FILE
        cmd = ""
        with open(schema_fn, "r") as f:
            for line in f:
                if line.strip() != "":
                    cmd = cmd + line
                    if(line.strip().endswith("FROM stdin;")):
                        continue
                    if(line.strip().endswith(";") or line.strip().endswith("\.")):
                        print (cmd)
                        cur.execute(cmd)
                        cmd = ""

        return ret

