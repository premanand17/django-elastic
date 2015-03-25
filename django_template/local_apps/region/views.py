from django.shortcuts import render
from search.elastic_model import Elastic
from django.conf import settings


def region_page(request, region):
    ''' Region search'''
    data = {"query": {"match": {"attr.region_id": region}}}
    elastic = Elastic(data, db=settings.REGIONDB)
    context = elastic.get_result()
    context['title'] = "Region"
    print(context)
    return render(request, 'region/region.html', context,
                  content_type='text/html')
