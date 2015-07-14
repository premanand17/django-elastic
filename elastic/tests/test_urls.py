''' Register TastyPie Elastic resources used for the tests only. '''
from django.conf.urls import include, url
from tastypie.api import Api
from elastic.tastypie.api import MarkerResource, GeneResource
from elastic.tests.settings_idx import IDX
from rest_framework import routers
from elastic.rest_framework.api import MarkerViewSet

# register tastypie api
api = Api(api_name='test')

# force the resources to use the test indices
marker = MarkerResource()
marker._meta.resource_name = IDX['MARKER']['indexName']
api.register(marker)
gene = GeneResource()
gene._meta.resource_name = IDX['GFF_GENERIC']['indexName']
api.register(gene)


router = routers.DefaultRouter()
router.register(r'marker_test', MarkerViewSet, base_name='marker_test')
MarkerViewSet.idx = IDX['MARKER']['indexName']


''' Tastypie test urls '''
urlpatterns = [url(r'^api/', include(api.urls)),
               url(r'^test_rest/', include(router.urls, namespace='rest-router')),
               ]
