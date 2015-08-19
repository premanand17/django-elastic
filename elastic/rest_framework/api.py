''' Django REST framework Elastic resources. '''
from rest_framework import serializers, viewsets, permissions
from elastic.rest_framework.resources import ListElasticMixin, ElasticLimitOffsetPagination,\
    RetrieveElasticMixin
from elastic.elastic_settings import ElasticSettings
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from pydgin_auth.permissions import check_has_permission
logger = logging.getLogger(__name__)


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
    # authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = PublicationSerializer
    pagination_class = ElasticLimitOffsetPagination
    idx = 'publications_v0.0.1'
    filter_fields = ('PMID', 'title', 'authors__LastName', 'tags__disease')

    def get(self, request):
        content = {
            'user': request.user,  # `django.contrib.auth.User` instance.
            'auth': request.auth,  # None
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


class PydginCustomMarkerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        print("checking has permission for {}".format(request.user))
        has_perm = check_has_permission(request.user, 'MARKER')
        print("Returning {} from PydginCustomMarkerPermission".format(has_perm))
        return has_perm


class MarkerViewSet(RetrieveElasticMixin, ListElasticMixin, viewsets.GenericViewSet):
    serializer_class = MarkerSerializer
    pagination_class = ElasticLimitOffsetPagination
    idx = resource_name = ElasticSettings.idx('MARKER', 'MARKER')
    filter_fields = ('seqid', 'id', 'start')
    # model = TheModel
    permission_classes = (PydginCustomMarkerPermission,)
