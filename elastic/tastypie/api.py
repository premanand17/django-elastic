''' TastyPie Elastic Index Resources. '''
from tastypie import fields, bundle, http
from tastypie.constants import ALL
from elastic.tastypie.resources import BaseGFFResource, ElasticObject,\
    ElasticResource
from elastic.elastic_settings import ElasticSettings
from tastypie.authorization import ReadOnlyAuthorization, DjangoAuthorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication
from tastypie.exceptions import TastypieError
from django_template import settings
from django.shortcuts import render_to_response
from django.http.response import HttpResponse


class GeneResource(BaseGFFResource):

    class Meta:
        resource_name = ElasticSettings.idx('GFF_GENES')
        object_class = ElasticObject
        #authentication = BasicAuthentication()
        authentication = ApiKeyAuthentication()
        #authorization = ReadOnlyAuthorization()
        authorization = DjangoAuthorization()
        max_limit = 100000
        filtering = {
            'attr': ['gene_name', 'gene_id', 'Name'],
            'seqid': ALL,
        }
        allowed_methods = ['get', 'post']
        
    def hydrate(self, bundle, request):
        bundle.obj.updated_by_id = request.user.id
        return bundle


class DiseaseResource(ElasticResource):
    tier = fields.IntegerField(attribute='tier', help_text='Tier')
    name = fields.CharField(attribute='name', help_text='Disease name')
    description = fields.CharField(attribute='description', help_text='Disease description')
    code = fields.CharField(attribute='code', help_text='Disease code')
    colour = fields.CharField(attribute='colour', help_text='Disease colour')

    class Meta:
        resource_name = ElasticSettings.idx('DISEASE')
        object_class = ElasticObject
        authorization = ReadOnlyAuthorization()
        max_limit = 100000
        filtering = {
            'tier': ALL,
            'name': ALL,
            'code': ALL,
        }
        allowed_methods = ['get', 'post']


class MarkerResource(ElasticResource):
    ''' Indexed dbSNP resource. '''

    # define the fields
    seqid = fields.CharField(attribute='seqid', help_text='Sequence identifier')
    start = fields.IntegerField(attribute='start', help_text='Reference position')
    id = fields.CharField(attribute='id', help_text='Unique identifier')
    ref = fields.CharField(attribute='ref', help_text='Reference bases')
    alt = fields.CharField(attribute='alt', help_text='Alternate bases')
    qual = fields.CharField(attribute='qual', help_text='Quality score')
    filter = fields.CharField(attribute='filter', help_text='Filter status')
    info = fields.CharField(attribute='info', help_text='Additional information')

    class Meta:
        resource_name = ElasticSettings.idx('MARKER', 'MARKER')
        object_class = ElasticObject
        authorization = ReadOnlyAuthorization()
        max_limit = 100000
        filtering = {
            'id': ALL,
            'seqid': ALL,
        }
        allowed_methods = ['get', 'post']
