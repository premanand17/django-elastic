from django.conf.urls import patterns, url
from genes import views

urlpatterns = patterns('genes',
                       url(r'^(?P<query>[-\w]+)/$', views.search),
                       )
