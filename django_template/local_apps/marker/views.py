from django.shortcuts import render
from es.views import elastic_search
from db.models import Featureloc


def marker_page(request, marker):

    data = {"query": {"match": {"id": marker}}}
    context = elastic_search(data)

    # get gene(s) overlapping position
    position = context['data'][0]['pos']
    chrom = 'chr'+context['data'][0]['src']
    featurelocs = (Featureloc.objects
                   .filter(fmin__lt=position)  # @UndefinedVariable
                   .filter(fmax__gt=position)  # @UndefinedVariable
                   .filter(srcfeature__uniquename=chrom)  # @UndefinedVariable
                   .filter(feature__type__name='gene'))  # @UndefinedVariable

    genes = []
    for loc in featurelocs:
        genes.append(loc.feature)
    context['genes'] = genes

    return render(request, 'marker/marker.html', context,
                  content_type='text/html')
