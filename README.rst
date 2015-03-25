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

3. Include the search URLconf in your project urls.py like this::

  url(r'^search/', include('search.urls', namespace="search")),
    
To run in DEBUG mode include the reverse proxy:

    if(settings.DEBUG):
        urlpatterns.append(url(r'^'+settings.MARKERDB+'|' +
                               settings.MARKERDB+',\w+/_search'+'|' +
                               settings.GENEDB + '|' +
                               settings.REGIONDB,
                               reverse_proxy),)
