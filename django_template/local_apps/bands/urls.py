from django.conf.urls import patterns, url
from bands import views

urlpatterns = patterns( 'bands',
    url(r'^cvlist/$', views.cvlist, name='cvlist'),
    url(r'^(?P<org>\w+)/$', views.cytobands, name='cytobands'),
    url(r'^cached/(?P<org>\w+)/$', views.cytobands2, name='cytobands2'),
)
