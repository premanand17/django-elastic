from django import template
from db.models import FeatureDbxref, FeatureSynonym

register = template.Library()


@register.inclusion_tag('gene/gene_section.html')
def show_gene_section(gene_feature):
    ''' Template tag to render a gene section given a chado gene feature. '''

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
