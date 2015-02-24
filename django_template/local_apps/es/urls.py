from django.conf.urls import patterns, url
from es import views

urlpatterns = patterns('es',
                       url(r'^(?P<query>[\w*]+)/$', views.search,
                           name='search'),
                       url(r'^(?P<src>\w+):(?P<start>[\w]+)-(?P<stop>[\w]+)/$',
                           views.range_search, name='range_search')
                       )
