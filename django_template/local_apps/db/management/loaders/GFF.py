from db.models import Cv, Cvterm, Cvtermprop, Feature, Featureloc, Featureprop
from db.models import Organism
import gzip
import re
import sys


class GFFManager:
    ''' GFF loader management '''

    def create_gff_disease_region_features(self, **options):
        ''' Create disease region features '''
        if options['org']:
            org = options['org']
        else:
            org = 'human'

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

                    # lookup disease short name
                    cv = Cv.objects.get(name='disease')
                    cvterm = Cvterm.objects.get(cv=cv, name=disease)
                    termtype = Cvterm.objects.get(name='disease short name')
                    cvtermprop = Cvtermprop.objects.get(cvterm=cvterm,
                                                        type=termtype)
                    disease_short = cvtermprop.value
                    print('disease... '+disease)
                continue

            parts = re.split('\t', line)
            if(len(parts) != 9):
                continue

            name = self._get_name(parts[8])
            uniquename = (parts[0] + "_" + name + "_" + parts[3] + "_" +
                          parts[4] + "_" + disease_short)
            feature = self._get_feature(name, uniquename, 'sequence',
                                        parts[2], organism)
            srcfeature = (Feature.objects
                          .filter(organism=organism)  # @UndefinedVariable
                          .get(uniquename=parts[0]))  # @UndefinedVariable
            print('get srcfeature... '+parts[0])
            fmin = int(parts[3])-1
            feature.save()
            featureloc = Featureloc(feature=feature, srcfeature=srcfeature,
                                    fmin=fmin, fmax=parts[4],
                                    locgroup=0, rank=0)
            featureloc.save()
            print('loaded feature... ' + feature.uniquename + ' on ' +
                  srcfeature.uniquename)

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
        termtype = Cvterm.objects.get(cv=cv, name=cvtermName)
        return Feature(organism=organism, name=name, uniquename=uniquename,
                       type=termtype, is_analysis=0, is_obsolete=0)


class GFF:
    ''' GFF file object - based on GFF3 specifications '''

    def __init__(self, line='dummy\tdummy\tregion\t' + str(sys.maxsize) +
                 '\t-1\t.\t.\t.\t\t'):
        parts = re.split('\t', line)
        if(len(parts) != 9):
            raise GFFError("GFF error: wrong number of columns")
        self.seqid = parts[0]
        self.source = parts[1]
        self.type = parts[2]
        self.start = int(parts[3])
        self.end = int(parts[4])
        self.score = parts[5]
        self.strand = parts[6]
        self.phase = parts[7]
        self.attrStr = parts[8]
        self.attrs = {}
        self._parseAttributes()

    def _parseAttributes(self):
        parts = re.split(';', self.attrStr)
        for p in parts:
            if(p == ''):
                continue
            at = re.split('=', p)
            if len(at) == 2:
                self.attrs[at[0]] = at[1]
            else:
                self.attrs[at[0]] = ""

    def getAttributes(self):
        return self.attrs


class GFFError(Exception):
    ''' GFF parse error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
