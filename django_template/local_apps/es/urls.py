from django.conf.urls import patterns, url
from es import views

urlpatterns = patterns( 'es',
    url(r'^$', views.search, name='search'),
    url(r'^(?P<query>\w+)/$', views.search2, name='search2'),
)
