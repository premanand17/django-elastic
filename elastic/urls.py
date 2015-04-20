from django.conf.urls import url
from elastic import views

urlpatterns = [
               # range overlap queries @IgnorePep8
               url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/$',
                   views.range_overlap_search, name='range_search'),
               url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/db/(?P<search_db>[\w]+)$',
                   views.range_overlap_search, name='filtered_range_search'),

               # query string
               url(r'^(?P<query>[\.\w*]+)/$', views.search, name='elastic'),
               url(r'^(?P<query>[\.\w*]+)/db/(?P<search_db>[\w]+)$',
                   views.search, name='filtered_search'),

               # count queries
               url(r'^(?P<query>[\.\w*]+)/db/(?P<search_db>[\w,]+)/(?P<ajax>[\w]+)',
                   views.ajax_search, name='count'),
               url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/db/(?P<search_db>[\w,]+)/(?P<ajax>[\w]+)',
                   views.ajax_range_overlap_search, name='filtered_range_search'),
               ]
