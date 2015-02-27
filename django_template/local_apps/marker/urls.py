from django.conf.urls import patterns, url
from marker import views

urlpatterns = patterns('marker',
                       url(r'^(?P<marker>[-\w]+)/$', views.marker_page,
                           name='marker_page'),
                       )
