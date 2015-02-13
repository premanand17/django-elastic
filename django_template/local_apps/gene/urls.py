from django.conf.urls import patterns, url
from gene import views

urlpatterns = patterns('genes',
                       url(r'^(?P<gene>[-\w]+)/$', views.gene_page),
                       )
