from db.models import Cvterm, Cvtermprop, Cv, Organism, Feature, Featureloc, Featureprop
from django.db import transaction
import gzip
import re

class GFFManager:

    def create_gff_features(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)

        disease = None
        disease_short = None
        organism = Organism.objects.get(common_name=org)
        if options['gff'].endswith('.gz'):
            f = gzip.open(options['gff'], 'rb')
        else:
            f = open(options['gff'], 'rb')
        
        
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
                    print('disease... '+disease)
                continue

            parts = re.split('\t', line)
            if(len(parts) != 9):
              continue

            name = self._get_name(parts[8])
            uniquename = parts[0]+"_"+name+"_"+parts[3]+"_"+parts[4]+"_"+disease_short
            feature = self._get_feature(name, uniquename, 'sequence', parts[2], organism) 
            srcfeature = Feature.objects.filter(organism=organism).get(uniquename=parts[0])
            print('get srcfeature... '+parts[0])
            fmin = int(parts[3])-1
            feature.save()
            featureloc = Featureloc(feature=feature, srcfeature=srcfeature, fmin=fmin, fmax=parts[4], locgroup=0, rank=0)
            featureloc.save()
            print('loaded feature... '+feature.uniquename+' on '+srcfeature.uniquename)
 
            if disease:
                cv = Cv.objects.get(name='disease')
                cvterm = Cvterm.objects.get(cv=cv, name=disease)
                feaureprop = Featureprop(feature=feature, type=cvterm, rank=0)
                feaureprop.save()
                print('loaded featureprop... '+disease)
        return
    
    def _get_name(self, attributes):
        parts = re.split(';', attributes)
        for part in parts:
            if(part.startswith('Name=')):
               return part[5:]
        return ""
    
    def _get_feature(self, name, uniquename, cvName, cvtermName, organism):
        cv = Cv.objects.get(name=cvName)
        type = Cvterm.objects.get(cv=cv,name=cvtermName)
        return Feature(organism=organism, name=name, uniquename=uniquename, type=type, is_analysis=0, is_obsolete=0)
   