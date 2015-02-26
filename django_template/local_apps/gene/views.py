from django.shortcuts import render
from db.models import Feature, Featureloc
from django.core.exceptions import ObjectDoesNotExist


def gene_page(request, gene):
    ''' Gene search'''
    try:
        feature = Feature.objects.get(uniquename=gene)  # @UndefinedVariable
    except ObjectDoesNotExist:
        context = {'error': 'Gene ('+gene+') not found.'}
        return render(request, 'gene/gene.html', context,
                      content_type='text/html')

    flocs = Featureloc.objects.filter(feature=feature)  # @UndefinedVariable
    locs = []
    for loc in flocs:
        locs.append(loc)
    context = {'feature': feature, 'locs': locs, 'gene': feature.uniquename}
    return render(request, 'gene/gene.html', context,
                  content_type='text/html')
