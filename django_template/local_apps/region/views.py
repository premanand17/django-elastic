from django.shortcuts import render
from es.views import elastic_search
from django.conf import settings


def region_page(request, region):
    ''' Region search'''
    data = {"query": {"match": {"attr.region_id": region}}}
    context = elastic_search(data, db=settings.REGIONDB)
    print(context)
    return render(request, 'region/region.html', context,
                  content_type='text/html')
