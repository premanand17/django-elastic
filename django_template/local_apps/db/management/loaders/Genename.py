from db.models import Cv, Cvterm, Feature, Organism, FeatureSynonym, Pub,\
    Synonym, Db, Dbxref, FeatureDbxref
import gzip
import re


class GenenameManager:

    def create_genename_features(self, **options):
        '''
        Create features based on genenames.org download file for names
        (http://www.genenames.org/cgi-bin/download).
        The file is assumed to include the following columns:
        hgnc id, approved symbol, status, locus type, previous symbols
        synonyms, entrez gene id, ensembl gene id
        '''
        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)

        if options['genenames'].endswith('.gz'):
            f = gzip.open(options['genenames'], 'rb')
        else:
            f = open(options['genenames'], 'rb')

        col = []
        synonymColumns = ["previous symbols", "synonyms",
                          "approved name",
                          "accession numbers", "locus type"]
        dbxrefColumns = ["entrez", "ensembl", "mgi", "refseq"]

        for line in f:
            parts = re.split('\t', line.decode("utf-8").rstrip())
            ''' Use table header to identify column names '''
            if(len(col) == 0):
                for part in parts:
                    col.append(part.lower()
                               .replace(' gene id', '')
                               .replace(' ids', '')
                               .replace('mouse genome database id', 'mgi'))
                continue

            columnDict = {}
            for idx, part in enumerate(parts):
                if part != '':
                    columnDict[col[idx]] = part

            if("status" in columnDict and columnDict["status"] == 'Approved'):
                print("loading... "+columnDict["approved symbol"])

                feature = self._get_feature(columnDict["hgnc id"][5:],
                                            columnDict["approved symbol"],
                                            'sequence', "gene", organism)
                feature.save()
                pub = Pub.objects.get(uniquename="null")

                for dbType in dbxrefColumns:
                    if(dbType in columnDict and
                       columnDict[dbType].strip() != ''):
                        # split and strip
                        dbxrefs = re.sub(r'\s', '',
                                         columnDict[dbType].strip()).split(',')
                        for acc in dbxrefs:
                            self._create_feature_dbxref(dbType, feature, acc)

                for synType in synonymColumns:
                    if(synType in columnDict):
                        syns = columnDict[synType].strip().split(',')
                        for syn in syns:
                            self._create_feature_synonym(syn, feature, pub)

    ''' Create a feature_synonym for a feature '''
    def _create_feature_synonym(self, synName, feature, pub):
        cv = Cv.objects.get(name='synonym_type')
        termtype = Cvterm.objects.get(cv=cv, name='exact')
        synonyms = Synonym.objects.filter(name=synName, type=termtype)
        if(len(synonyms) == 0):
            synonym = Synonym(name=synName, type=termtype,
                              synonym_sgml=synName)
            synonym.save()
        else:
            synonym = synonyms[0]

        feature_synonyms = FeatureSynonym.objects.filter(feature=feature,
                                                         synonym=synonym,
                                                         pub=pub)
        if len(feature_synonyms) == 0:
            feature_synonym = FeatureSynonym(feature=feature, synonym=synonym,
                                             pub=pub, is_current=True)
            feature_synonym.save()

    def _create_feature_dbxref(self, dbName, feature, acc):
        ''' Create a feature_dbxref for a feature '''
        dbs = Db.objects.filter(name=dbName)
        if(len(dbs) == 0):
            db = Db(name=dbName)
            db.save()
        else:
            db = dbs[0]
        dbxrefs = Dbxref.objects.filter(db=db, accession=acc)
        if len(dbxrefs) == 0:
            dbxref = Dbxref(db=db, accession=acc)
            dbxref.save()
        else:
            dbxref = dbxrefs[0]
        feature_dbxrefs = FeatureDbxref.objects.filter(dbxref=dbxref,
                                                       feature=feature)
        if len(feature_dbxrefs) == 0:
            feature_dbxref = FeatureDbxref(dbxref=dbxref, feature=feature)
            feature_dbxref.save()

    def _get_feature(self, name, uniquename, cvName, cvtermName, organism):
        ''' Get a new feature object '''
        cv = Cv.objects.get(name=cvName)
        termtype = Cvterm.objects.get(cv=cv, name=cvtermName)
        return Feature(organism=organism, name=name, uniquename=uniquename,
                       type=termtype, is_analysis=0, is_obsolete=0)
