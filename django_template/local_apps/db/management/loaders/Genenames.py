from db.models import Cv, Cvterm, Feature, Organism, FeatureSynonym, Pub,\
    Synonym, Db, Dbxref, FeatureDbxref
import gzip
import re


class GenenameManager:

    '''
    Create features based on genenames.org. The file is assumed to include the
    following columns:
    hgnc id
    approved symbol
    status
    locus type
    previous symbols
    synonyms
    entrez gene id
    ensembl gene id
    '''
    def create_genename_features(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)

        if options['genenames'].endswith('.gz'):
            f = gzip.open(options['genenames'], 'rb')
        else:
            f = open(options['genenames'], 'rb')

#         col = ["hgnc", "symbol", "name", "status", "loc_type", "prev_sym",
#                "syns", "chr", "acc", "entrez", "ensembl", "mg_id",
#                "PMID", "refseq"]
        col = []
        synonymColumns = ["previous symbols", "syns", "acc"]
        dbxrefColumns = ["entrez", "ensembl", "mg_id", "refseq"]

        for line in f:
            parts = re.split('\t', line.decode("utf-8").rstrip())

            ''' Use table header to identify column names '''
            if(len(col) == 0):
                for part in parts:
                    col.append(part.lower().replace(' gene id', ''))

            syn = {}
            for idx, part in enumerate(parts):
                syn[col[idx]] = part

            if("status" in syn and syn["status"] == 'Approved'):
                print("loading... "+syn["approved symbol"]+"\t" +
                      syn["locus type"]+"\t" +
                      syn["previous symbols"]+"\t"+syn["synonyms"])

                feature = self._get_feature(syn["hgnc id"][5:],
                                            syn["approved symbol"],
                                            'sequence', "gene", organism)
                feature.save()
                pub = Pub.objects.get(uniquename="null")

                for dbType in dbxrefColumns:
                    if(dbType in syn and syn[dbType].strip() != ''):
                        # split and strip
                        dbxrefs = re.sub(r'\s', '',
                                         syn[dbType].strip()).split(',')
                        for acc in dbxrefs:
                            self._create_feature_dbxref(dbType, feature, acc)

                for synType in synonymColumns:
                    if(synType in syn and syn[synType].strip() != ''):
                        # split and strip
                        syns = re.sub(r'\s', '',
                                      syn[synType].strip()).split(',')
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
        feature_synonym = FeatureSynonym(feature=feature, synonym=synonym,
                                         pub=pub, is_current=True)
        feature_synonym.save()

    ''' Create a feature_dbxref for a feature '''
    def _create_feature_dbxref(self, dbName, feature, acc):
        dbs = Db.objects.filter(name=dbName)
        if(len(dbs) == 0):
            db = Db(name=dbName)
            db.save()
        else:
            db = dbs[0]
        dbxref = Dbxref(db=db, accession=acc)
        dbxref.save()
        feature_dbxref = FeatureDbxref(dbxref=dbxref, feature=feature)
        feature_dbxref.save()

    ''' Get a new feature object '''
    def _get_feature(self, name, uniquename, cvName, cvtermName, organism):
        cv = Cv.objects.get(name=cvName)
        termtype = Cvterm.objects.get(cv=cv, name=cvtermName)
        return Feature(organism=organism, name=name, uniquename=uniquename,
                       type=termtype, is_analysis=0, is_obsolete=0)
