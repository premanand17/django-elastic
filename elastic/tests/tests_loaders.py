from django.test import TestCase
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, IDX_UPDATE
import requests
import time
from elastic.management.loaders.utils import GFF, GFFError
from elastic.elastic_settings import ElasticSettings
from elastic.management.snapshot import Snapshot
from elastic.elastic_model import Search


def setUpModule():
    ''' Run the index loading script to create test indices '''
    for idx_kwargs in IDX.values():
        call_command('index_search', **idx_kwargs)
    time.sleep(2)
    for idx_kwargs in IDX_UPDATE.values():
        call_command('index_search', **idx_kwargs)


def tearDownModule():
    ''' Remove loaded test indices '''
    for key in IDX:
        requests.delete(ElasticSettings.url() + '/' + IDX[key]['indexName'])


class SnapshotTest(TestCase):
    ''' Test elastic snapshot and restore. '''

    def test_show(self, snapshot=None):
        call_command('show_snapshot')
        call_command('show_snapshot', all=True)

    def test_create_delete_repository(self):
        repos = 'test_backup'
        self.assertFalse(Snapshot.exists(repos, ''), 'Repository '+repos+' not yet created')
        call_command('repository', repos, dir="/tmp/test_snapshot/")
        self.assertTrue(Snapshot.exists(repos, ''), 'Repository '+repos+' created')
        call_command('repository', repos, delete=True)
        self.assertFalse(Snapshot.exists(repos, ''), 'Repository '+repos+' deleted')

    def test_create_restore_delete_snapshot(self):
        snapshot = 'test_'+ElasticSettings.getattr('TEST')

        # create a snapshot
        call_command('snapshot', snapshot, indices=IDX['MARKER']['indexName'])
        self.assertTrue(Snapshot.exists(ElasticSettings.getattr('REPOSITORY'), snapshot),
                        "Created snapshot "+snapshot)

        # delete index
        requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])
        self.assertFalse(Search.index_exists(IDX['MARKER']['indexName']), "Removed index")
        # restore from snapshot
        call_command('restore_snapshot', snapshot)
        self.assertTrue(Search.index_exists(IDX['MARKER']['indexName']), "Restored index exists")

        # remove snapshot
        call_command('snapshot', snapshot, delete=True)
        self.assertFalse(Snapshot.exists(ElasticSettings.getattr('REPOSITORY'), snapshot),
                         "Deleted snapshot "+snapshot)


class ElasticLoadersTest(TestCase):

    def test_idx_loader(self):
        ''' Test loader has created and populated indices.  '''
        for key in IDX:
            idx = IDX[key]['indexName']
            self.assertTrue(Search.index_exists(idx=idx), 'Index exists: '+idx)

            # check the index has documents, allow for the indexing to complete if necessary
            ndocs = 0
            for _ in range(3):
                ndocs = Search(idx=idx).get_count()['count']
                if ndocs > 0:
                    break
                time.sleep(1)
            self.assertTrue(ndocs > 0, "Elastic count documents in " + idx + ": " + str(ndocs))

    def test_utils(self):
        ''' Test gff utils. '''
        line = "chr22\tt1dbase\tvariant\t37191071\t37191071\t.\t+\t.\tName=rs229533;region_id=36"
        gff = GFF(line)
        attrs = gff.getAttributes()
        self.assertTrue('Name' in attrs, "GFF attributes parse")
        line = '1\thavana\texon\t137682\t137965\t.\t-\t.\tgene_id "ENSG00000269981"; gene_version "1";'
        gff = GFF(line, key_value_delim=' ')
        attrs = gff.getAttributes()
        self.assertTrue('gene_id' in attrs, "GFF attributes parse")

        # check for gff errors
        line = "chr22\tt1dbase\tvariant\t37191071\t37191071\t.\t+\t."
        self.assertRaises(GFFError, GFF, line=line)
