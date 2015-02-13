from django.shortcuts import render
from es.views import _getContext


def marker_page(request, marker):

    data = {"query": {"match": {"ID": marker}}}
    context = _getContext(data)
    return render(request, 'marker/marker.html', context,
                  content_type='text/html')
