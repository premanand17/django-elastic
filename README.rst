======
Search
======

Search is a Django app to run Elastic search queries.

Quick start
-----------

1. Installation
pip install -e git://github.com/D-I-L/django-search.git#egg=search

2. Add "search" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'search',
    )

3. Add the URL of your Elasticsearch to the settings.py::

# elastic search engine
SEARCH_ELASTIC_URL = 'http://127.0.0.1:9200/'

4. Include the search URLconf in your project urls.py like this::

  url(r'^search/', include('search.urls', namespace="search")),
