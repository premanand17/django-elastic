from django.conf.urls import patterns, url
from marker import views

urlpatterns = patterns('gene',
                       url(r'^(?P<marker>[-\w]+)/$', views.marker_page),
                       )
