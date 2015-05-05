from tastypie.constants import ALL
from elastic.tastypie.resources import BaseGFFResource, ElasticObject,\
    ElasticResource
from tastypie import fields


class GeneResource(BaseGFFResource):

    class Meta:
        resource_name = 'grch37_75_genes'
        object_class = ElasticObject
        max_limit = 100000
        filtering = {
            'attr': ['gene_name', 'gene_id'],
            'seqid': ALL,
        }


class GwasBarrettResource(BaseGFFResource):

    class Meta:
        resource_name = 'gb2_hg19_gwas_t1d_barrett_4_17_0'
        object_class = ElasticObject
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
        resource_name = 'dbsnp142'
        object_class = ElasticObject
        max_limit = 100000
        filtering = {
            'id': ALL,
            'seqid': ALL,
        }
