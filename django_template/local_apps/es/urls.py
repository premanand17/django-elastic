from django.conf.urls import patterns, url
from es import views

urlpatterns = patterns('es',
                       url(r'^(?P<query>\w+)/$', views.search, name='search'),
                       url(r'^wildcard/(?P<query>\w+)/$', views.wildcard,
                           name='wildcard'),
                       )
