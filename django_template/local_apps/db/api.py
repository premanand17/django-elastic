from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from db.models import Cvterm, Cv, Cvtermprop, Feature, Featureloc, Featureprop
from db.models import Organism


class CvResource(ModelResource):
    class Meta:
        queryset = Cv.objects.all()
        filtering = {"name": ALL}
        cache = SimpleCache(timeout=100)


class CvtermFullResource(ModelResource):
    cv = fields.ForeignKey(CvResource, 'cv')
    cvtermprops = fields.ToManyField('db.api.CvtermpropResource',
                                     'cvtermprop_cvterm', full=True, null=True)

    class Meta:
        queryset = Cvterm.objects.select_related("cv")
        excludes = ['is_relationshiptype']
        filtering = {"cv": ALL_WITH_RELATIONS,
                     "is_obsolete": ALL,
                     "name": ALL}
        cache = SimpleCache(timeout=100)


class CvtermResource(ModelResource):
    cv = fields.ForeignKey(CvResource, 'cv')

    class Meta:
        queryset = Cvterm.objects.select_related("cv")
        excludes = ['is_relationshiptype']
        filtering = {"cv": ALL_WITH_RELATIONS,
                     "is_obsolete": ALL,
                     "name": ALL}
        cache = SimpleCache(timeout=100)


class CvtermpropResource(ModelResource):
    cvterm = fields.ForeignKey(CvtermResource, 'cvterm',
                               related_name='cvtermprop_cvterm')
    type_id = fields.ForeignKey(CvtermResource, 'type',
                                related_name='cvtermprop_type')

    class Meta:
        queryset = Cvtermprop.objects.all()


class OrganismResource(ModelResource):
    class Meta:
        queryset = Organism.objects.all()
        resource_name = 'organism'
        filtering = {"common_name": ALL}


class FeatureFullResource(ModelResource):
    '''
    Resource of all features
    '''
    featurelocs = fields.ToManyField('db.api.FeaturelocResource',
                                     'featureloc_feature',
                                     related_name='featureloc_feature',
                                     full=True)
    featureprop = fields.ToManyField('db.api.FeaturepropResource',
                                     'featureprop_set', full=True)
    type = fields.ForeignKey(CvtermResource, 'type', full=True)
    organism = fields.ForeignKey(OrganismResource, 'organism', full=True)

    class Meta:
        queryset = Feature.objects.all()  # @UndefinedVariable
        excludes = ['residues', 'md5checksum', 'timeaccessioned',
                    'timelastmodified', 'is_analysis', 'is_obsolete']
        filtering = {'uniquename': ALL,
                     'type': ALL_WITH_RELATIONS,
                     'organism': ALL_WITH_RELATIONS,
                     'featurelocs': ALL_WITH_RELATIONS,
                     'featureprop': ALL_WITH_RELATIONS,
                     }


class FeatureResource(ModelResource):
    '''
    Resource of all features
    '''
    type = fields.ForeignKey(CvtermResource, 'type')
    organism = fields.ForeignKey(OrganismResource, 'organism')

    class Meta:
        queryset = Feature.objects.all()  # @UndefinedVariable
        excludes = ['residues', 'md5checksum', 'timeaccessioned',
                    'timelastmodified', 'is_analysis', 'is_obsolete']
        filtering = {
            'uniquename': ALL,
            'type': ALL_WITH_RELATIONS,
            'organism': ALL_WITH_RELATIONS,
        }


class FeaturelocResource(ModelResource):
    ''' Resource of all featurelocs '''
    feature = fields.ForeignKey(FeatureResource, 'feature',
                                related_name='featureloc_feature', null=True)
    srcfeature = fields.ForeignKey(FeatureResource, 'srcfeature',
                                   related_name='featureloc_srcfeature',
                                   null=True)

    class Meta:
        queryset = Featureloc.objects.all()  # @UndefinedVariable
        filtering = {
            'feature': ALL_WITH_RELATIONS,
            'srcfeature': ALL_WITH_RELATIONS,
        }


class FeaturelocFullResource(ModelResource):
    ''' Resource of all featurelocs '''
    feature = fields.ForeignKey(FeatureResource, 'feature',
                                full=True)
    srcfeature = fields.ForeignKey(FeatureResource, 'srcfeature', null=True)

    class Meta:
        queryset = (Featureloc.objects
                    .select_related("feature",  # @UndefinedVariable
                                    "srcfeature"))
        excludes = ['is_fmax_partial', 'is_fmin_partial',
                    'locgroup', 'residue_info', 'phase']
        filtering = {
            'feature': ALL_WITH_RELATIONS,
            'srcfeature': ALL_WITH_RELATIONS,
        }


class FeaturepropResource(ModelResource):
    ''' Resource of all featureprops '''
    feature = fields.ForeignKey(FeatureResource, 'feature')
    type = fields.ForeignKey(CvtermResource, 'type', full=True)

    class Meta:
        queryset = Featureprop.objects.all()
        filtering = {
            'rank': ALL,
            'feature': ALL_WITH_RELATIONS,
            'type': ALL_WITH_RELATIONS,
        }


class FeaturepropFullResource(ModelResource):
    ''' Resource of all featureprops '''
    feature = fields.ForeignKey(FeatureFullResource, 'feature', full=True)
    type = fields.ForeignKey(CvtermFullResource, 'type', full=True)

    class Meta:
        resource_name = 'featurepropfull'
        queryset = Featureprop.objects.all()
        filtering = {
            'rank': ALL,
            'feature': ALL_WITH_RELATIONS,
            'type': ALL_WITH_RELATIONS,
        }
