from rest_framework import serializers, viewsets
from elastic.rest_framework.resources import ListElasticMixin


class PublicationSerializer(serializers.Serializer):

    class PublicationAuthor(serializers.Serializer):
        ForeName = serializers.StringRelatedField()
        LastName = serializers.StringRelatedField()
        Initials = serializers.StringRelatedField()

    PMID = serializers.IntegerField()
    title = serializers.StringRelatedField()
    abstract = serializers.StringRelatedField()
    journal = serializers.StringRelatedField()
    authors = serializers.ListField(child=PublicationAuthor())
    date = serializers.DateField()
    tags__disease = serializers.ListField(child=serializers.StringRelatedField())


class PublicationViewSet(ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = PublicationSerializer
    idx = 'publications_v0.0.1'
    filter_fields = ('PMID', 'title', 'authors__LastName')
