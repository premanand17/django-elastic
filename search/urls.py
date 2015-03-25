from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('search',
                       url(r'^(?P<query>[\.\w*]+)/$', views.search, name='search'),
                       url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/$',
                           views.range_overlap_search, name='range_search'),
                       url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/db/(?P<search_db>[\w]+)$',
                           views.range_overlap_search, name='filtered_range_search'),
                       url(r'^(?P<query>[\.\w*]+)/db/(?P<search_db>[\w]+)$',
                           views.search, name='filtered_search')
                       )
