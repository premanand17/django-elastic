from django.conf.urls import patterns, include, url
from db.api import CvtermResource, CvtermFullResource, CvResource
from db.api import CvtermpropResource, FeaturelocResource
from db.api import FeaturelocFullResource, FeatureResource, FeatureFullResource
from db.api import FeaturepropResource, FeaturepropFullResource
from db.api import OrganismResource
from tastypie.api import Api
from django_template import settings
from search.views import reverse_proxy

# register tastypie api
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
                       url(r'^', include('bands.urls', namespace="bands")),
                       url(r'^api/', include(api.urls)),
                       url(r'^search/', include('search.urls', namespace="search")),
                       url(r'^gene/', include('gene.urls')),
                       url(r'^marker/', include('marker.urls')),
                       url(r'^region/', include('region.urls')),
                       )

if(settings.DEBUG):
    urlpatterns.append(url(r'^'+settings.MARKERDB+'|' +
                           settings.MARKERDB+',\w+/_search'+'|' +
                           settings.GENEDB + '|' +
                           settings.REGIONDB,
                           reverse_proxy),)
