from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from db.models import Feature, Featureloc, Featureprop, Cv, Cvterm

import logging, re
# Get an instance of a logger
logger = logging.getLogger(__name__)

def cvlist(request):
    cv_list = Cv.objects.all()
    context = {'cv_list': cv_list}
    return render(request, 'bands/cvlist.html', context)

# 60 mins cache
@cache_page(60 * 60)
def cytobands(request, org):
    #bands = Featureloc.objects.getCytoBands(org)

    srcfeatureIds = Featureloc.objects.getSrcFeatures(org)
    srcfeatures = Feature.objects.filter(featureloc_srcfeature=srcfeatureIds)
    
    # order by chr number  (assumes chr prefix)
    srcfeatures = sorted(srcfeatures, key=lambda srcfeature: (int(srcfeature.uniquename.replace("chr", ""))
                         if srcfeature.uniquename.replace("chr", "").isnumeric() else 1000))

    cv = Cv.objects.get(name="DIL")
    cvtermDIL = Cvterm.objects.filter(cv=cv)

    context = {'srcfeatures': srcfeatures, 
               'org':org,
               'cvtermDIL':cvtermDIL }
    return render(request, 'bands/bands.html', context, content_type='text/html')

# 60 mins cache
@cache_page(60 * 60)
def cytobands2(request, org):
    bands = Featureloc.objects.getCytoBands(org)
    srcfeatureIds = bands.distinct('srcfeature_id')
    srcfeatures = Feature.objects.filter(featureloc_srcfeature=srcfeatureIds)
    
    # order by chr number (assumes chr prefix)
    srcfeatures = sorted(srcfeatures, key=lambda srcfeature: (int(srcfeature.uniquename.replace("chr", ""))
                         if srcfeature.uniquename.replace("chr", "").isnumeric() else 1000))

    cv = Cv.objects.get(name="DIL")
    cvtermDIL = Cvterm.objects.filter(cv=cv)

    context = {'bands': bands, 'srcfeatures': srcfeatures, 'org':org, 'cvtermDIL':cvtermDIL}
    return render(request, 'bands/bands2.html', context)

