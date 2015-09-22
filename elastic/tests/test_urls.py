''' Register rest framework Elastic resources used for the tests only. '''
from django.conf.urls import include, url
from elastic.tests.settings_idx import IDX
from rest_framework import routers
from elastic.rest_framework.api import MarkerViewSet


router = routers.DefaultRouter()
router.register(r'marker_test', MarkerViewSet, base_name='marker_test')
MarkerViewSet.idx = IDX['MARKER']['indexName']


''' Tastypie test urls '''
urlpatterns = [
        url(r'^test_rest/', include(router.urls, namespace='rest-router')),
    ]
