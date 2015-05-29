from elastic.elastic_settings import ElasticSettings
import requests
import json
import logging
import os

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Snapshot():
    ''' Show, create and delete Elastic snapshots. '''

    @classmethod
    def exists(cls, repo, snapshot):
        ''' Test if the repository/snapshot exists. '''
        url = ElasticSettings.url() + '/_snapshot/' + repo + '/' + snapshot
        resp = requests.get(url)
        if resp.status_code != 200:
            return False
        else:
            return True

    @classmethod
    def show(cls, repo, snapshots, all_repos):
        ''' Show the information for the named snapshots. '''
        if all_repos:
            repo = ''
            snapshots = ''
        url = ElasticSettings.url() + '/_snapshot/' + repo + '/' + snapshots
        resp = requests.get(url)
        if resp.status_code != 200:
            logger.error("Returned status (for "+url+"): "+str(resp.status_code))
            logger.error(resp.json()["error"])
        else:
            print(json.dumps(resp.json(), indent=4))

    @classmethod
    def create_repository(self, repo, location):
        url = ElasticSettings.url() + '/_snapshot/' + repo
        if Snapshot.exists(repo, ''):
            logger.error("Repository "+repo+" already exists!")
            return False
        parent = os.path.abspath(os.path.join(location, ".."))

        if not os.path.isdir(parent):
            logger.warn("Check directory exists: "+parent)

        data = {"type": "fs",
                "settings": {"location": location}
                }
        resp = requests.put(url, data=json.dumps(data))
        if resp.status_code != 200:
            logger.error("Status ("+url+"): "+str(resp.status_code) + " :: " + resp.json()["error"])
        return True

    @classmethod
    def delete_repository(cls, repo):
        url = ElasticSettings.url() + '/_snapshot/' + repo
        resp = requests.delete(url)
        if resp.status_code != 200:
            logger.error("Status ("+url+"): "+str(resp.status_code) + " :: " + resp.json()["error"])
            return False
        return True

    @classmethod
    def create_snapshot(cls, repo, snapshot, indices):
        ''' Create a snapshot for the specified indices or all if
        indices is None. '''
        url = ElasticSettings.url() + '/_snapshot/' + repo + '/' + snapshot + '?wait_for_completion=true'
        resp = requests.get(url)
        if resp.status_code == 200:
            logger.error("Snapshot "+snapshot+" already exists!")
            return False

        data = {}
        if indices is not None:
            data = {"indices": indices}
        resp = requests.put(url, data=json.dumps(data))
        if resp.status_code != 200:
            logger.error("Snapshot "+snapshot+" create error! :: " + resp.json()["error"])
        return True

    @classmethod
    def delete_snapshot(cls, repo, snapshot):
        url = ElasticSettings.url() + '/_snapshot/' + repo + '/' + snapshot
        resp = requests.delete(url)
        if resp.status_code != 200:
            logger.error("Status ("+url+"): "+str(resp.status_code) + " :: " + resp.json()["error"])

    @classmethod
    def restore_snapshot(cls, repo, snapshot, url, indices):
        url += '/_snapshot/' + repo + '/' + snapshot + '/_restore'
        data = {}
        if indices is not None:
            data = {"indices": indices}
        resp = requests.post(url, data=json.dumps(data))
        if resp.status_code != 200:
            logger.error("Status ("+url+"): "+str(resp.status_code) + " :: " + resp.json()["error"])
