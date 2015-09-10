''' Update manager to update indexes '''
from elastic.search import Search, ScanAndScroll, ElasticQuery
from elastic.management.loaders.loader import Loader
import sys
import json
import logging
from elastic.query import Query
import random
import timeit

# Get an instance of a logger
logger = logging.getLogger(__name__)

JSON_LINES = ""
IDX_NAME = ""
IDX_TYPE = ""


def fetch_update(resp_json):
    '''
    Docs are fetched in chunks of 500 (chunk size) and for each doc, update api is called
    with the newly added contents from JSON_LINES
    '''
    logger.debug('fetch update called')
    global JSON_LINES
    global IDX_NAME
    global IDX_TYPE

    global START_TIME
    global END_TIME
    global TIME_TAKEN

    line_num = 0
    auto_num = 1
    json_data = ''
    chunk = 500
    try:
        for doc in resp_json['hits']['hits']:
            doc_data = {"update": {"_id": doc["_id"], "_type": IDX_TYPE, "_index": IDX_NAME, "_retry_on_conflict": 3}}
            json_data += json.dumps(doc_data) + '\n'
            json_data += json.dumps(JSON_LINES) + '\n'

            line_num += 1
            auto_num += 1

            if(line_num > chunk):
                line_num = 0
                print('.', end="", flush=True)
                Loader().bulk_load(IDX_NAME, IDX_TYPE, json_data)
                json_data = ''

    finally:
        Loader().bulk_load(IDX_NAME, IDX_TYPE, json_data)
        pass

    END_TIME = timeit.default_timer()
    TIME_TAKEN = END_TIME - START_TIME
    logger.debug('Total time taken ' + str(TIME_TAKEN))


class UpdateManager(Loader):

    def update_idx(self, **options):

        '''
        The data to be added to the existing doc is taken from json_data option and saved in global JSON_LINES
        scan_and_scroll (pulls batches of results from Elasticsearch until there are no more results left),
        and the actual update is done by fetch_update method
        Use random updates option for testing only
        '''

        global JSON_LINES
        global IDX_NAME
        global IDX_TYPE
        # idx_name = 'region_perms_test_idx'
        IDX_NAME = options['indexName']
        IDX_TYPE = options['indexType']
        logger.debug("Index name " + IDX_NAME)
        logger.debug("Index type " + IDX_TYPE)

        f = self.open_file_to_load('json_data', **options)

        lines = ''
        try:
            for line in f:
                lines += line.decode("utf-8").rstrip()

            JSON_LINES = json.loads(lines)

            if options['random_update']:
                logger.debug('Random updates')
                self.do_random_idx_updates(JSON_LINES, **options)
            else:
                logger.debug('Complete updates')
                ScanAndScroll.scan_and_scroll(IDX_NAME, call_fun=fetch_update, idx_type=IDX_TYPE)
        except:
            logger.debug("Unexpected error:", sys.exc_info()[0])

    def do_random_idx_updates(self, JSON_LINES, **options):
        '''
        Random ids are generated, docs are searched for those ids, and if docs present they are updated...ONLY for TEST
        '''
        logger.debug("Random update called")
        global START_TIME

        START_TIME = timeit.default_timer()
        print("START TIME" + str(START_TIME))

        min_int = 1
        max_int = 111373853

        random_ids = []
        for x in range(0, 10000):
            random_id = random.randint(min_int, max_int)
            random_ids.append(random_id)

        logger.debug('Number of ids for ' + str(x) + ' iterations ' + str(len(random_ids)))

        logger.debug(random_ids)
        query = ElasticQuery(Query.ids(random_ids))
        elastic = Search(query, size=1000000, idx=options['indexName'], idx_type=options['indexType'])
        resp_count = elastic.get_count()
        logger.debug('Response count ' + str(resp_count['count']))
        json_resp = elastic.get_json_response()
        fetch_update(json_resp)
