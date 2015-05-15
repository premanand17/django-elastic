from tastypie import fields
from tastypie.constants import ALL
from elastic.tastypie.resources import BaseGFFResource, ElasticObject,\
    ElasticResource
from elastic.elastic_settings import ElasticSettings
from tastypie.authorization import ReadOnlyAuthorization


class GeneResource(BaseGFFResource):

    class Meta:
        resource_name = ElasticSettings.idx('GFF_GENES')
        object_class = ElasticObject
        authorization = ReadOnlyAuthorization()
        max_limit = 100000
        filtering = {
            'attr': ['gene_name', 'gene_id', 'Name'],
            'seqid': ALL,
        }
        allowed_methods = ['get', 'post']


class GwasBarrettResource(BaseGFFResource):

    class Meta:
        resource_name = 'gb2_hg19_gwas_t1d_barrett_4_17_0'
        object_class = ElasticObject
        authorization = ReadOnlyAuthorization()
        max_limit = 100000
        filtering = {
            'attr': ['gene_name', 'gene_id'],
            'seqid': ALL,
        }
        allowed_methods = ['get', 'post']


class MarkerResource(ElasticResource):

    # define the fields
    seqid = fields.CharField(attribute='seqid', help_text='Sequence identifier')
    start = fields.IntegerField(attribute='start', help_text='Refernce position')
    id = fields.CharField(attribute='id', help_text='Unique indentifier')
    ref = fields.CharField(attribute='ref', help_text='Reference bases')
    alt = fields.CharField(attribute='alt', help_text='Alternate bases')
    qual = fields.CharField(attribute='qual', help_text='Quality score')
    filter = fields.CharField(attribute='filter', help_text='Filter status')
    info = fields.CharField(attribute='info', help_text='Additional information')

    class Meta:
        resource_name = ElasticSettings.idx_only('MARKER')
        object_class = ElasticObject
        authorization = ReadOnlyAuthorization()
        max_limit = 100000
        filtering = {
            'id': ALL,
            'seqid': ALL,
        }
        allowed_methods = ['get', 'post']
