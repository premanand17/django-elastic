from django.shortcuts import render
from db.models import Feature, FeatureDbxref, FeatureSynonym, Featureloc
from django.core.exceptions import ObjectDoesNotExist


def search(request, query):
    ''' Gene search'''
    try:
        feature = Feature.objects.get(uniquename=query)  # @UndefinedVariable
    except ObjectDoesNotExist:
        context = {'error': 'Gene ('+query+') not found.'}
        return render(request, 'genes/genes.html', context,
                      content_type='text/html')

    feature_dbxrefs = FeatureDbxref.objects.filter(feature=feature)
    dbxrefs = []
    for feature_dbxref in feature_dbxrefs:
        dbxrefs.append(feature_dbxref.dbxref)

    feature_synonyms = FeatureSynonym.objects.filter(feature=feature)
    synonyms = []
    for feature_synonym in feature_synonyms:
        synonyms.append(feature_synonym.synonym)

    flocs = Featureloc.objects.filter(feature=feature)  # @UndefinedVariable
    locs = []
    for loc in flocs:
        locs.append(loc)
    context = {'feature': feature, 'dbxrefs': dbxrefs,
               'synonyms': synonyms, 'locs': locs}
    return render(request, 'genes/genes.html', context,
                  content_type='text/html')
