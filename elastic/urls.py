from django.conf.urls import url, include
from elastic import views
from tastypie.api import Api
from elastic.tastypie.api import GeneResource, GwasBarrettResource,\
    MarkerResource

# register tastypie api
api = Api(api_name='dev')
api.register(GeneResource())
api.register(GwasBarrettResource())
api.register(MarkerResource())

urlpatterns = [
               # range overlap queries @IgnorePep8
               url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/$',
                   views.range_overlap_search, name='range_search'),
               url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/db/(?P<search_idx>[\w]+)$',
                   views.range_overlap_search, name='filtered_range_search'),

               # query string
               url(r'^(?P<query>[\.\w*]+)/$', views.search, name='elastic'),
               url(r'^(?P<query>[\.\w*]+)/db/(?P<search_idx>[\w]+)$',
                   views.search, name='filtered_search'),

               # count queries
               url(r'^(?P<query>[\.\w*]+)/db/(?P<search_idx>[\w,]+)/(?P<ajax>[\w]+)',
                   views.ajax_search, name='count'),
               url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/db/(?P<search_idx>[\w,]+)/(?P<ajax>[\w]+)',
                   views.ajax_range_overlap_search, name='filtered_range_search'),

               url(r'^api/', include(api.urls), name='elastic'),
               ]
