# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from datetime import datetime 

class Cv(models.Model):
    cv_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    definition = models.TextField(blank=True)

    def __str__(self):
       return self.name

    class Meta:
       managed = False
       db_table = 'cv'


class Cvprop(models.Model):
    cvprop_id = models.IntegerField(primary_key=True)
    cv = models.ForeignKey(Cv)
    type = models.ForeignKey('Cvterm')
    value = models.TextField(blank=True)
    rank = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cvprop'
 


class Cvterm(models.Model):
    cvterm_id = models.AutoField(primary_key=True)
    cv = models.ForeignKey(Cv)
    name = models.CharField(max_length=1024)
    definition = models.TextField(blank=True)
    dbxref = models.ForeignKey('Dbxref', unique=True)
    is_obsolete = models.IntegerField()
    is_relationshiptype = models.IntegerField()

    def __str__(self):
       return self.name

    class Meta:
       managed = False
       db_table = 'cvterm'



class CvtermDbxref(models.Model):
    cvterm_dbxref_id = models.IntegerField(primary_key=True)
    cvterm = models.ForeignKey(Cvterm)
    dbxref = models.ForeignKey('Dbxref')
    is_for_definition = models.IntegerField()

    class Meta:
       managed = False
       db_table = 'cvterm_dbxref'


class CvtermRelationship(models.Model):
    cvterm_relationship_id = models.IntegerField(primary_key=True)
    type = models.ForeignKey(Cvterm, related_name='cvterm_relationship_type')
    subject = models.ForeignKey(Cvterm, related_name='cvterm_relationship_subject')
    object = models.ForeignKey(Cvterm, related_name='cvterm_relationship_object')

    class Meta:
        managed = False
        db_table = 'cvterm_relationship'
        
        
class Cvtermpath(models.Model):
    cvtermpath_id = models.IntegerField(primary_key=True)
    type = models.ForeignKey(Cvterm, blank=True, null=True, related_name='cvtermpath_type')
    subject = models.ForeignKey(Cvterm, related_name='cvtermpath_subject')
    object = models.ForeignKey(Cvterm, related_name='cvtermpath_object')
    cv = models.ForeignKey(Cv, related_name='cvtermpath_cv')
    pathdistance = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cvtermpath'


class Cvtermprop(models.Model):
    cvtermprop_id = models.AutoField(primary_key=True)
    cvterm = models.ForeignKey(Cvterm, related_name='cvtermprop_cvterm')
    type = models.ForeignKey(Cvterm, related_name='cvtermprop_type')
    value = models.TextField()
    rank = models.IntegerField()

    class Meta:
       managed = False
       db_table = 'cvtermprop'



class Cvtermsynonym(models.Model):
    cvtermsynonym_id = models.IntegerField(primary_key=True)
    cvterm = models.ForeignKey(Cvterm, related_name='cvtermsynonym_cvterm')
    synonym = models.CharField(max_length=1024)
    type = models.ForeignKey(Cvterm, blank=True, null=True, related_name='cvtermsynonym_type')
 
    class Meta:
        managed = False
        db_table = 'cvtermsynonym'


class Db(models.Model):
    db_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True)
    urlprefix = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)

    class Meta:
       managed = False
       db_table = 'db'



class Dbxref(models.Model):
    dbxref_id = models.AutoField(primary_key=True)
    db = models.ForeignKey(Db)
    accession = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
       managed = False
       db_table = 'dbxref'



class FeatureQuerySet(models.QuerySet):
    def getByUniquename(self, uniquename):
        return self.get(uniquename=uniquename)

    def getCytoBands(self, org):
        cv = Cv.objects.get(name='gstain')
        cvterms = Cvterm.objects.filter(cv=cv)
        organism = Organism.objects.filter(common_name=org)
        return self.filter(type=cvterms, organism=organism)

class Feature(models.Model):
    feature_id = models.AutoField(primary_key=True)
    dbxref = models.ForeignKey(Dbxref, blank=True, null=True)
    organism = models.ForeignKey('Organism')
    name = models.CharField(max_length=255, blank=True)
    uniquename = models.TextField()
    residues = models.TextField(blank=True)
    seqlen = models.IntegerField(blank=True, null=True)
    md5checksum = models.CharField(max_length=32, blank=True)
    type = models.ForeignKey(Cvterm)
    is_analysis = models.BooleanField(default=False)
    is_obsolete = models.BooleanField(default=False)
    timeaccessioned = models.DateTimeField(default=datetime.now, blank=True)
    timelastmodified = models.DateTimeField(default=datetime.now, blank=True)
    objects = FeatureQuerySet.as_manager()
    
    class Meta:
        managed = False
        db_table = 'feature'
 

       
class FeaturelocQuerySet(models.QuerySet):

    def getCytoBands(self, org):
        featureBands = Feature.objects.getCytoBands(org)
        return self.filter(feature=featureBands)

    def getSrcFeatures(self, org):
        organism = Organism.objects.filter(common_name=org)
        return self.filter(srcfeature=Feature.objects.filter(organism=organism)).distinct('srcfeature_id')
    
class Featureloc(models.Model):
    featureloc_id = models.AutoField(primary_key=True)
    feature = models.ForeignKey(Feature, related_name="featureloc_feature")
    srcfeature = models.ForeignKey(Feature, blank=True, null=True, related_name="featureloc_srcfeature")
    fmin = models.IntegerField(blank=True, null=True)
    is_fmin_partial = models.BooleanField(default=False)
    fmax = models.IntegerField(blank=True, null=True)
    is_fmax_partial = models.BooleanField(default=False)
    strand = models.SmallIntegerField(blank=True, null=True)
    phase = models.IntegerField(blank=True, null=True)
    residue_info = models.TextField(blank=True)
    locgroup = models.IntegerField()
    rank = models.IntegerField()
    objects = FeaturelocQuerySet.as_manager()

    class Meta:
        managed = False
        db_table = 'featureloc'
 
        
class Featureprop(models.Model):
    featureprop_id = models.AutoField(primary_key=True)
    feature = models.ForeignKey(Feature)
    type = models.ForeignKey(Cvterm)
    value = models.TextField(blank=True)
    rank = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'featureprop'
 


class Organism(models.Model):
    organism_id = models.IntegerField(primary_key=True)
    abbreviation = models.CharField(max_length=255, blank=True)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
       return self.common_name
   
    class Meta:
        managed = False
        db_table = 'organism'
 


