''' Django REST framework Elastic resources. '''
from rest_framework import serializers, viewsets
from elastic.rest_framework.resources import ListElasticMixin, ElasticLimitOffsetPagination,\
    RetrieveElasticMixin
from elastic.elastic_settings import ElasticSettings
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class PublicationSerializer(serializers.Serializer):
    ''' Publication resource. '''

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


class PublicationViewSet(RetrieveElasticMixin, ListElasticMixin, viewsets.GenericViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = PublicationSerializer
    pagination_class = ElasticLimitOffsetPagination
    idx = 'publications_v0.0.1'
    filter_fields = ('PMID', 'title', 'authors__LastName', 'tags__disease')

    def get(self, request):
        content = {
            'user': unicode(request.user),  # `django.contrib.auth.User` instance.
            'auth': unicode(request.auth),  # None
        }
        return Response(content)


class DiseaseSerializer(serializers.Serializer):
    ''' Disease resource. '''
    tier = serializers.IntegerField(help_text='Tier')
    name = serializers.CharField(help_text='Disease name')
    description = serializers.CharField(help_text='Disease description')
    code = serializers.CharField(help_text='Disease code')
    colour = serializers.CharField(help_text='Disease colour')


class DiseaseViewSet(RetrieveElasticMixin, ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = DiseaseSerializer
    pagination_class = ElasticLimitOffsetPagination
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


class MarkerViewSet(RetrieveElasticMixin, ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = MarkerSerializer
    pagination_class = ElasticLimitOffsetPagination
    idx = resource_name = ElasticSettings.idx('MARKER', 'MARKER')
    filter_fields = ('seqid', 'id', 'start')
