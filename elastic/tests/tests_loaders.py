''' Tests for command line interface for managing Elastic repositories,
defining mappings for indices and loading/indexing data. '''
from django.test import TestCase
from django.core.management import call_command
from elastic.tests.settings_idx import IDX, IDX_UPDATE
import requests
from elastic.management.loaders.utils import GFF, GFFError
from elastic.elastic_settings import ElasticSettings
from elastic.management.snapshot import Snapshot
from elastic.search import Search


def setUpModule():
    ''' Run the index loading script to create test indices and
    create test repository '''
    for idx_kwargs in IDX.values():
        call_command('index_search', **idx_kwargs)

    # wait for the elastic load to finish
    for key in IDX:
        Search.wait_for_load(IDX[key]['indexName'])

    for idx_kwargs in IDX_UPDATE.values():
        call_command('index_search', **idx_kwargs)

    # create test repository
    call_command('repository', SnapshotTest.TEST_REPO, dir=SnapshotTest.TEST_REPO_DIR)


def tearDownModule():
    ''' Remove loaded test indices and test repository. '''
    for key in IDX:
        requests.delete(ElasticSettings.url() + '/' + IDX[key]['indexName'])
    call_command('repository', SnapshotTest.TEST_REPO, delete=True)


class SnapshotTest(TestCase):
    ''' Test elastic snapshot and restore. '''

    TEST_REPO = 'test_backup_'+ElasticSettings.getattr('TEST')
    TEST_REPO_DIR = "/tmp/test_snapshot/"

    def test_show(self, snapshot=None):
        call_command('show_snapshot')
        call_command('show_snapshot', all=True)

    def test_create_delete_repository(self):
        repo = SnapshotTest.TEST_REPO
        self.assertTrue(Snapshot.exists(repo, ''), 'Repository '+repo+' created')

        self.assertFalse(Snapshot.create_repository(repo, SnapshotTest.TEST_REPO_DIR),
                         'Repository already exists.')

        call_command('repository', repo, delete=True)
        self.assertFalse(Snapshot.exists(repo, ''), 'Repository '+repo+' deleted')
        self.assertFalse(Snapshot.delete_repository(repo), 'Repository '+repo+' deleted')
        call_command('repository', repo, dir=SnapshotTest.TEST_REPO_DIR)
        self.assertTrue(Snapshot.exists(repo, ''), 'Repository '+repo+' created')

    def test_create_restore_delete_snapshot(self):
        snapshot = 'test_'+ElasticSettings.getattr('TEST')
        repo = SnapshotTest.TEST_REPO

        # create a snapshot
        call_command('snapshot', snapshot, indices=IDX['MARKER']['indexName'], repo=repo)
        Snapshot.wait_for_snapshot(repo, snapshot)
        self.assertTrue(Snapshot.exists(repo, snapshot), "Created snapshot "+snapshot)

        # delete index
        requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])
        self.assertFalse(Search.index_exists(IDX['MARKER']['indexName']), "Removed index")
        # restore from snapshot
        call_command('restore_snapshot', snapshot, repo=repo)
        Search.wait_for_load(IDX['MARKER']['indexName'])
        self.assertTrue(Search.index_exists(IDX['MARKER']['indexName']), "Restored index exists")

        # remove snapshot
        call_command('snapshot', snapshot, delete=True, repo=repo)
        Snapshot.wait_for_snapshot(repo, snapshot, delete=True, count=10)
        self.assertFalse(Snapshot.exists(repo, snapshot), "Deleted snapshot "+snapshot)

    def test_create_snapshot(self):
        snapshot = 'test_'+ElasticSettings.getattr('TEST')
        repo = SnapshotTest.TEST_REPO
        call_command('snapshot', snapshot, indices=IDX['MARKER']['indexName'], repo=repo)
        Snapshot.wait_for_snapshot(repo, snapshot)

        # snapshot already exist so return false
        self.assertFalse(Snapshot.create_snapshot(repo, snapshot, IDX['MARKER']['indexName']))
        # remove snapshot
        call_command('snapshot', snapshot, delete=True, repo=repo)
        self.assertFalse(Snapshot.exists(repo, snapshot),
                         "Deleted snapshot "+snapshot)


class ElasticLoadersTest(TestCase):

    def test_idx_loader(self):
        ''' Test loader has created and populated indices.  '''
        for key in IDX:
            idx = IDX[key]['indexName']
            # check the index has documents, allow for the indexing to complete if necessary
            Search.wait_for_load(idx)
            self.assertTrue(Search.index_exists(idx=idx), 'Index exists: '+idx)
            ndocs = Search(idx=idx).get_count()['count']
            self.assertTrue(ndocs > 0, "Elastic count documents in " + idx + ": " + str(ndocs))

    def test_mapping(self):
        ''' Test mapping used in GFF loader. '''
        idx = IDX['GFF_GENERIC']['indexName']
        mapping_json = Search(idx=idx).get_mapping()
        self.assertFalse('error' in mapping_json, 'No error returned from mapping request.')
        self.assertTrue('mappings' in mapping_json[idx], 'Found mappings.')
        seqid = mapping_json[idx]['mappings']['gff']['properties']['seqid']
        self.assertTrue('not_analyzed' == seqid['index'], 'seqid in GFF is not_analyzed')

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
