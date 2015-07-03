from rest_framework import serializers, viewsets
from elastic.rest_framework.resources import ListElasticMixin
from elastic.elastic_settings import ElasticSettings


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


class DiseaseSerializer(serializers.Serializer):
    tier = serializers.IntegerField(help_text='Tier')
    name = serializers.CharField(help_text='Disease name')
    description = serializers.CharField(help_text='Disease description')
    code = serializers.CharField(help_text='Disease code')
    colour = serializers.CharField(help_text='Disease colour')


class DiseaseViewSet(ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = DiseaseSerializer
    idx = 'disease'
    filter_fields = ('name', 'code')


class MarkerSerializer(serializers.Serializer):
    ''' Indexed dbSNP resource. '''

    seqid = serializers.CharField(help_text='Sequence identifier')
    start = serializers.IntegerField(help_text='Reference position')
    id = serializers.CharField(help_text='Unique identifier')
    ref = serializers.CharField(help_text='Reference bases')
    alt = serializers.CharField(help_text='Alternate bases')
    qual = serializers.CharField(help_text='Quality score')
    filter = serializers.CharField(help_text='Filter status')
    info = serializers.CharField(help_text='Additional information')


class MarkerViewSet(ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = MarkerSerializer
    idx = resource_name = ElasticSettings.idx('MARKER', 'MARKER')
    filter_fields = ('seqid', 'id', 'start')
