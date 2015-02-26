from django import template
from db.models import FeatureDbxref, FeatureSynonym
from es.views import elastic_search
from django_template import settings

register = template.Library()


@register.inclusion_tag('gene/gene_section.html')
def show_gene_section(gene_feature):
    ''' Template inclusion tag to render a gene section given a
    chado gene feature. '''

    feature_dbxrefs = FeatureDbxref.objects.filter(feature=gene_feature)
    gene_dbxrefs = []
    for feature_dbxref in feature_dbxrefs:
        gene_dbxrefs.append(feature_dbxref.dbxref)

    feature_synonyms = FeatureSynonym.objects.filter(feature=gene_feature)
    gene_synonyms = []
    for feature_synonym in feature_synonyms:
        gene_synonyms.append(feature_synonym.synonym)

    return {'feature': gene_feature,
            'synonyms': gene_synonyms,
            'dbxrefs': gene_dbxrefs}


@register.inclusion_tag('gene/es_gene_section.html')
def show_es_gene_section(gene_symbol=None, seqid=None, pos=None):
    ''' Template inclusion tag to render a gene section given a
    chado gene feature. '''

    if gene_symbol is not None:
        ''' gene symbol query'''
        data = {"query": {"match": {"gene_symbol": gene_symbol}}}
    else:
        ''' range query '''
        must = [{"match": {"seqid": 'chr'+seqid}},
                {"range": {"featureloc.start": {"lte": pos, "boost": 2.0}}},
                {"range": {"featureloc.end": {"gte": pos, "boost": 2.0}}}]
        query = {"bool": {"must": must}}
        data = {"query": query}

    es_result = elastic_search(data, db=settings.GENEDB)
    return {'es_genes': es_result["data"]}
