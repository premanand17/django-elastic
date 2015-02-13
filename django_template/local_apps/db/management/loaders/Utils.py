from db.models import Cvterm, Cv, Dbxref, Db, Organism, FeatureDbxref, Feature, \
    Featureloc
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import logging
import gzip
from db.management.loaders import GFF

# Get an instance of a logger
logger = logging.getLogger(__name__)


class UtilsManager:

    ''' Create CV and cvterms. '''
    def create_cvterms(self, cvName, cvDefn, termList):

        try:
            cv = Cv.objects.get(name=cvName)
            logger.warn("WARNING:: " + cvName + " CV EXISTS")
        except ObjectDoesNotExist:
            logger.warn("WARNING:: ADD " + cvName + " CV")
            cv = Cv(name=cvName, definition=cvDefn)
            cv.save()

        db = Db.objects.get(name='null')
        for term in termList:
            try:
                dbxref = Dbxref(db_id=db.db_id, accession=term.name)
                dbxref.save()
                cvterm = Cvterm(dbxref_id=dbxref.dbxref_id, cv_id=cv.cv_id,
                                name=term.name, definition=term.definition,
                                is_obsolete=0, is_relationshiptype=0)
                cvterm.save()
            except IntegrityError:
                logger.warn("WARNING:: " + term.name + " FAILED TO LOAD")
        return cv

    '''
    For existing features in the database, create featurelocs
    based on transcript ranges.
    '''
    def create_refseq_features(self, **options):

        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)

        if options['gff_refseq'].endswith('.gz'):
            f = gzip.open(options['gff_refseq'], 'rb')
        else:
            f = open(options['gff_refseq'], 'rb')

        genes = {}
        for line in f:
            gff = GFF(line.decode("utf-8").rstrip())

            if(gff.type != 'CDS'):
                continue

            attrs = gff.getAttributes()
            if(attrs['EntrezGene'] in genes):
                gene = genes[attrs['EntrezGene']]
                if(gene.start > gff.start):
                    gene.start = gff.start
                if(gene.end < gff.end):
                    gene.end = gff.end
            else:
                genes[attrs['EntrezGene']] = gff
        # load gene spans
        for key in genes:
            gene = genes[key]
            print(gene.seqid + ' ' + str(gene.start) + '..' +
                  str(gene.end) + ' ' +
                  gene.getAttributes()['Native_id'] + ' ' +
                  gene.getAttributes()['EntrezGene'])
            dbxrefs = Dbxref.objects.filter(accession=
                                            gene.getAttributes()['EntrezGene'])
            if len(dbxrefs) == 0:
                continue

            feature_dbxrefs = (FeatureDbxref
                               .objects.filter(dbxref=dbxrefs[0]))
            if len(feature_dbxrefs) == 0:
                continue

            feature = feature_dbxrefs[0].feature
            srcfeature = (Feature.objects
                          .filter(organism=organism)  # @UndefinedVariable
                          .get(uniquename=gene.seqid))  # @UndefinedVariable
            featureloc = Featureloc(feature=feature, srcfeature=srcfeature,
                                    fmin=gene.start - 1, fmax=gene.end,
                                    locgroup=0, rank=0)
            featureloc.save()
