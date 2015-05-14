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


class MarkerResource(ElasticResource):

    # define the fields
    seqid = fields.CharField(attribute='seqid')
    start = fields.IntegerField(attribute='start')
    id = fields.CharField(attribute='id')
    ref = fields.CharField(attribute='ref')
    alt = fields.CharField(attribute='alt')
    qual = fields.CharField(attribute='qual')
    filter = fields.CharField(attribute='filter')
    info = fields.CharField(attribute='info')

    class Meta:
        resource_name = ElasticSettings.idx_only('MARKER')
        object_class = ElasticObject
        authorization = ReadOnlyAuthorization()
        max_limit = 100000
        filtering = {
            'id': ALL,
            'seqid': ALL,
        }
