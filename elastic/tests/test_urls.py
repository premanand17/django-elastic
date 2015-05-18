''' Register TastyPie Elastic resources used for the tests only. '''
from django.conf.urls import include, url
from tastypie.api import Api
from elastic.tastypie.api import MarkerResource, GeneResource
from elastic.tests.settings_idx import IDX

# register tastypie api
api = Api(api_name='test')

# force the resources to use the test indices
marker = MarkerResource()
marker._meta.resource_name = IDX['MARKER']['indexName']
api.register(marker)
gene = GeneResource()
gene._meta.resource_name = IDX['GFF_GENERIC']['indexName']
api.register(gene)

''' Tastypie test urls '''
urlpatterns = [url(r'^api/', include(api.urls)),
               ]
