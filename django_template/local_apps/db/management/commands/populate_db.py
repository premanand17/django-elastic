from django.core.management.base import BaseCommand
from db.models import Cvterm, Cvtermprop, Cv, Db, Dbxref, Organism, Feature, Featureloc, Featureprop
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import gzip
import re
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to populate the database \n" \
      "python manage.py populate_db --gff loaded/Hs_GRCh38-T1D-assoc_tableGFF.txt.gz  --org human_GRCh38\n" \
      "python manage.py populate_db --bands loaded/mouse_ideogram.gz --org mouse_mm10\n" \
      "python manage.py populate_db --disease loaded/disease.list"
    
    option_list = BaseCommand.option_list + (
        make_option('--disease',
            dest='disease',
            help='Add disease terms'),
        ) + (
        make_option('--bands',
            dest='bands',
            help='Add cytological bands'),
        ) + (
        make_option('--org',
            dest='org',
            help='Organism'),
        ) + (
        make_option('--gff',
            dest='gff',
            help='GFF file of features'),
        ) + (
        make_option('--chr',
            dest='chr',
            help='Chromosome sequence lengths'),
        )

    def _get_name(self, attributes):
        parts = re.split(';', attributes)
        for part in parts:
            if(part.startswith('Name=')):
               return part[5:]
        return ""

    def _create_disease_cvterms(self, **options):
        
        dilList = []
        dilList.append(Cvterm(name='disease short name', definition=''))
        dilList.append(Cvterm(name='colour', definition=''))
        self._create_cvterms("DIL", "DIL terms", dilList)
        dil_cv = Cv.objects.get(name="DIL")

        # read disease list as two column tab delimited file
        f = open(options['disease'], 'r')
        for line in f:
            if(line.startswith("#")):
                continue
            termList = []
            parts = re.split('\t', line)
            termList.append(Cvterm(name=parts[0], definition=parts[1]))
            self._create_cvterms("disease", "disease types", termList)

            cv = Cv.objects.get(name="disease")
            cvterm = Cvterm.objects.get(cv=cv, name=parts[0])
            type = Cvterm.objects.get(cv=dil_cv, name='colour')
            Cvtermprop(cvterm=cvterm, type=type, value=parts[3].rstrip(), rank=0).save()
            type = Cvterm.objects.get(cv=dil_cv, name='disease short name')
            Cvtermprop(cvterm=cvterm, type=type, value=parts[2], rank=parts[4]).save()

                              
    '''
    Set up the G-staining ontology and return the CV object
    '''
    def _gstain(self):
        gstainList = []
        gstains = [ 'gpos100', 'gpos', 'gpos75', 'gpos66', 'gpos50', 'gpos33', 'gpos25', 'gvar', 'gneg', 'acen', 'stalk' ]
        for gstain in gstains:
            gstainList.append(Cvterm(name=gstain, definition=gstain))
        return self._create_cvterms("gstain", "Giemsa banding", gstainList)


    '''
    Create CV and cvterms
    '''
    def _create_cvterms(self, cvName, cvDefn, termList):
        try:
            cv = Cv.objects.get(name=cvName)
            logger.warn("WARNING:: "+cvName+" CV EXISTS")
        except ObjectDoesNotExist as e:
            logger.warn("WARNING:: ADD "+cvName+" CV")
            cv = Cv(name=cvName, definition=cvDefn)
            cv.save()
        
        db = Db.objects.get(name='null')
        for term in termList:
            try:
                dbxref = Dbxref(db_id=db.db_id, accession=term.name)
                dbxref.save()
                cvterm = Cvterm(dbxref_id=dbxref.dbxref_id, cv_id=cv.cv_id, name=term.name, definition=term.definition, is_obsolete=0, is_relationshiptype=0)
                cvterm.save()
            except IntegrityError as ee:
                logger.warn("WARNING:: "+term.name+" FAILED TO LOAD")
        return cv

    '''
    Create cytological band features
    '''
    def _create_bands(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'
 
        cv = self._gstain()
        organism = Organism.objects.get(common_name=org)
        f = gzip.open(options['bands'], 'rb')
        for line in f:
            #self.stdout.write(line.decode("utf-8"))
            parts = re.split('\t', line.decode("utf-8"))
            name = parts[0]+'_'+parts[3]
            try:
              cvterm = Cvterm.objects.get(cv=cv, name=parts[4].rstrip())
              feature = Feature(organism=organism, uniquename=name, name=parts[3], type=cvterm, is_analysis=0, is_obsolete=0)
              self.stdout.write('create feature... '+name+' on '+parts[0])
              srcfeature = Feature.objects.get(organism=organism, uniquename=parts[0])
              self.stdout.write('get srcfeature... '+parts[0])
              fmin = int(parts[1])-1
              feature.save()
              featureloc = Featureloc(feature=feature, srcfeature=srcfeature, fmin=fmin, fmax=parts[2], locgroup=0, rank=0)
              featureloc.save()
              self.stdout.write('loaded feature... '+name+' on '+srcfeature.uniquename)
            except ObjectDoesNotExist as e:
              logger.warn("WARNING:: NOT LOADED "+name)
              logger.warn(e)
        return

    def _create_chr_features(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)
        self.stdout.write('organism... '+organism.common_name)

        cv = Cv.objects.get(name='sequence')
        cvterm = Cvterm.objects.get(cv=cv, name='chromosome')
        self.stdout.write(cvterm.name)

        f = gzip.open(options['chr'], 'rb')
        for line in f:
            line = line.decode("utf-8")
            parts = re.split('\t', line)
            if '_' in parts[0]:
                continue
            uniquename = parts[0]
            name = uniquename
            seqlen = parts[1]
            f = Feature(organism=organism, name=name, uniquename=uniquename, type=cvterm, is_analysis=0, is_obsolete=0, seqlen=seqlen)
            f.save()


    def _create_gff_features(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)

        disease = None
        disease_short = None
        organism = Organism.objects.get(common_name=org)
        f = gzip.open(options['gff'], 'rb')
        for line in f:
            line = line.decode("utf-8")
            if(line.startswith("##")):
                if(line.startswith("##Key Disease:")):
                    disease = line[14:].strip()
                    #disease_short = "".join(item[0].upper() for item in disease.split())

                    # lookup disease short name
                    cv = Cv.objects.get(name='disease')
                    cvterm = Cvterm.objects.get(cv=cv, name=disease)
                    type = Cvterm.objects.get(name='disease short name')
                    cvtermprop = Cvtermprop.objects.get(cvterm=cvterm, type=type)
                    disease_short = cvtermprop.value
                    self.stdout.write('disease... '+disease)
                continue

            parts = re.split('\t', line)
            if(len(parts) != 9):
              continue

            name = self._get_name(parts[8])
            uniquename = parts[0]+"_"+name+"_"+parts[3]+"_"+parts[4]+"_"+disease_short
            feature = self._get_feature(name, uniquename, 'sequence', parts[2], organism) 
            srcfeature = Feature.objects.filter(organism=organism).get(uniquename=parts[0])
            self.stdout.write('get srcfeature... '+parts[0])
            fmin = int(parts[3])-1
            feature.save()
            featureloc = Featureloc(feature=feature, srcfeature=srcfeature, fmin=fmin, fmax=parts[4], locgroup=0, rank=0)
            featureloc.save()
            self.stdout.write('loaded feature... '+feature.uniquename+' on '+srcfeature.uniquename)
 
            if disease:
                cv = Cv.objects.get(name='disease')
                cvterm = Cvterm.objects.get(cv=cv, name=disease)
                feaureprop = Featureprop(feature=feature, type=cvterm, rank=0)
                feaureprop.save()
                self.stdout.write('loaded featureprop... '+disease)
        return

    def _get_feature(self, name, uniquename, cvName, cvtermName, organism):
        cv = Cv.objects.get(name=cvName)
        type = Cvterm.objects.get(cv=cv,name=cvtermName)
        return Feature(organism=organism, name=name, uniquename=uniquename, type=type, is_analysis=0, is_obsolete=0)

    def handle(self, *args, **options):
        if options['disease']:
          self._create_disease_cvterms(**options)
        elif options['bands']:
          self._create_bands(**options)
        elif options['gff']:
          self._create_gff_features(**options)
        elif options['chr']:
          self._create_chr_features(**options)


