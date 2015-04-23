======
Search
======

Search is a Django app to run Elastic search queries.

Quick start
-----------

1. Installation::

    pip install -e git://github.com/D-I-L/django-elastic.git#egg=elastic

2. Add "search" to your ``INSTALLED_APPS`` in ``settings.py``::

    INSTALLED_APPS = (
        ...
        'elastic',
    )

3. Add the settings to the settings.py::

    # elastic search engine
    ELASTIC = {
        'default': {
            'ELASTIC_URL': 'http://127.0.0.1:9200/',
            'IDX': {
                'MARKER': 'dbsnp142',
                'DEFAULT': 'dbsnp142',
             },
            'TEST': 'test_suffix',
            'REPOSITORY': 'my_backup',
       }
    }

4. Include the search URLconf in your project urls.py like this::

    url(r'^search/', include('elastic.urls', namespace="elastic")),

  
Snapshot and Restore
--------------------

The `snapshot and restore Elastic module`_ is used by the custom ``django-elastic``
management commands described below. These can be used in creating and managing
repositories containing snapshots of indices. ::

    ./manage.py show_snapshot --help
    ./manage.py snapshot --help
    ./manage.py repository --help
    ./manage.py restore_snapshot --help

Note that apart from the ``repository`` argument each command takes a ``--repo``
flag to specify the repository name. If the ``--repo`` flag is not provided the
``REPOSITORY`` defined in the ``ELASTIC`` setting in ``settings.py`` is used.

.. _snapshot and restore Elastic module: http://www.elastic.co/guide/en/elasticsearch/reference/current/modules-snapshots.html 

Create/Delete Repository
~~~~~~~~~~~~~~~~~~~~~~~~

The ``repository`` argument is used in the creation and deletion of a
repository. To **create** a 'test_backup' repository::

    ./manage.py repository test_backup --dir /path_to_backup/snapshot/test_snapshot/

To **delete** the 'test_backup' repository::

    ./manage.py repository test_backup --delete

Create/Delete Snapshot
~~~~~~~~~~~~~~~~~~~~~~
The ``snapshot`` argument is used is used in the creation and
deletion of a snapshot. To **create** a 'snapshot_1' snapshot of the
indices 'disease_region_grch38' and 'disease'::

    ./manage.py snapshot snapshot_1 --indices disease_region_grch38,disease

To **delete** the 'snapshot_1' snapshot::

    ./manage.py snapshot snapshot_1 --delete

Restore To Another Elastic Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To copy a snapshot to an instance of Elastic on the **same network**, use
the ``url`` flag to point at the other cluster to copy to::

    ./manage.py restore_snapshot snapshot_1 --repo tmp_restore \
                       --url http://cluster_host:9200

A repository can be used to copy indices to another cluster that is on 
a **different network**. To do this tar and move data to the machine with 
the cluster to copy the indices to. Un-tar and ensure the directory has 
read-write permissions for everyone (note that for a multi-nodes cluster
make sure the file system repository is available to all nodes - /tmp
is fine for a temporary single node cluster)::

    tar cvf /tmp/snapshot_test/test_snapshot.tar  test_snapshot/
    chmod a+rwx -R test_snapshot

Change the ``REPOSITORY`` and ``ELASTIC_URL`` settings in Django to
point at the correct Elastic cluster. Then create a new repository 
that points to the snapshot repository::

    ./manage.py repository tmp_restore --dir /tmp/snapshot_test/test_snapshot/

View the repository and snapshot::

    ./manage.py show_snapshot --repo tmp_restore
    ./manage.py show_snapshot --all

Now use ``restore_snapshot`` to copy the data from the repository::
 
    ./manage.py restore_snapshot snapshot_1 --repo tmp_restore \
                       --url http://localhost:9200

The URL parameter can be used to copy to other Elastic instances on
the network. Now list the available indices to check that they have
been created::

    curl 'http://localhost:9200/_cat/indices?v'

**Delete** the repository and remove the data::

    ./manage.py repository tmp_restore --delete
    rm -rf /tmp/snapshot_test/
 