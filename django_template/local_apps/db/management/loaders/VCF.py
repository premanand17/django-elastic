from db.models import Cvterm, Cv, Organism, Feature, Featureloc
from django.db import transaction
import gzip
import re


class VCFManager:

    def create_vcf_features(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'
        organism = Organism.objects.get(common_name=org)
        cv = Cv.objects.get(name='sequence')
        cvterm = Cvterm.objects.get(cv=cv, name='SNP')

        if options['vcf'].endswith('.gz'):
            f = gzip.open(options['vcf'], 'rb')
        else:
            f = open(options['vcf'], 'rb')

        lastSrc = ""
        n = 0
        transaction.set_autocommit(False)

        try:
            for line in f:
                line = line.decode("utf-8")
                parts = re.split('\t', line)
                if(len(parts) != 8 or line.startswith("#")):
                    continue

                chrom = 'chr'+parts[0]
                fmax = int(parts[1])
                fmin = fmax - 1
                uniquename = parts[2]

                if(lastSrc != parts[0]):
                    print('loading SNPs on: ' +
                          chrom, end=" ...", flush=True)
                    srcfeature = (Feature.objects
                                  .filter(organism=organism)  # @UndefinedVariable @IgnorePep8
                                  .get(uniquename=chrom))  # @UndefinedVariable
                lastSrc = parts[0]

                feature = Feature(organism=organism, uniquename=uniquename,
                                  type=cvterm, is_analysis=0, is_obsolete=0)
                feature.save()

                rank = 0
                Featureloc(feature=feature, srcfeature=srcfeature,
                           fmin=fmin, fmax=fmax, locgroup=0, rank=rank,
                           residue_info=parts[3]).save()

                alts = re.split(',', parts[4])
                for alt in alts:
                    rank += 1
                    Featureloc(feature=feature, srcfeature=srcfeature,
                               fmin=fmin, fmax=fmax, locgroup=0, rank=rank,
                               residue_info=alt).save()

                n += 1
                if(n > 1999):
                    n = 0
                    print('.', end="", flush=True)
                    transaction.commit()

            transaction.commit()
        finally:
            transaction.set_autocommit(True)

        return
