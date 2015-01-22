from django.conf.urls import patterns, include, url
from django.contrib import admin
from db.api import CvtermResource, CvtermFullResource, CvResource, CvtermpropResource, FeaturelocResource, FeaturelocFullResource, FeatureResource, FeatureFullResource, FeaturepropResource, FeaturepropFullResource, OrganismResource
from tastypie.api import Api

api = Api(api_name='dev')
api.register(CvtermResource())
api.register(CvtermFullResource())
api.register(CvResource())
api.register(OrganismResource())
api.register(FeaturelocResource())
api.register(FeaturelocFullResource())
api.register(FeatureResource())
api.register(FeatureFullResource())
api.register(FeaturepropResource())
api.register(FeaturepropFullResource())
api.register(CvtermpropResource())


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_template.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('bands.urls', namespace="bands")),
    url(r'^api/', include(api.urls)),
    url(r'^search/', include('es.urls', namespace="es")),
)

