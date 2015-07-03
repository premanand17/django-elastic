from rest_framework import serializers, viewsets
from elastic.rest_framework.resources import ListElasticMixin


class PublicationSerializer(serializers.Serializer):
    ''' Publication serializer '''

    class PublicationAuthor(serializers.Serializer):
        ForeName = serializers.ReadOnlyField()
        LastName = serializers.ReadOnlyField()
        Initials = serializers.ReadOnlyField()

    PMID = serializers.IntegerField()
    title = serializers.ReadOnlyField()
    abstract = serializers.ReadOnlyField()
    journal = serializers.ReadOnlyField()
    authors = serializers.ListField(child=PublicationAuthor())
    date = serializers.DateField()
    tags = serializers.DictField()


class PublicationViewSet(ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = PublicationSerializer
    idx = 'publications_v0.0.1'
    filter_fields = ('PMID', 'title', 'authors__LastName', 'tags__disease')
