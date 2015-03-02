from django.conf.urls import patterns, url
from region import views

urlpatterns = patterns('region',
                       url(r'^(?P<region>[-\w]+)/$',
                           views.region_page, name='region_page'),
                       )
