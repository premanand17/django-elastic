from django.core.management.base import BaseCommand
from db.models import Cvterm, Cvtermprop, Cv, Db, Dbxref, Organism, Feature, Featureloc, Featureprop
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import gzip
import re
import logging
from db.management.loaders.VCF import VCFManager
from db.management.loaders.GFF import GFFManager
from db.management.loaders.Bands import BandsManager
from db.management.loaders.Utils import create_cvterms


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Use to populate the database \n" \
      "python manage.py populate_db --gff loaded/Hs_GRCh38-T1D-assoc_tableGFF.txt.gz  --org human_GRCh38\n" \
      "python manage.py populate_db --bands loaded/mouse_ideogram.gz --org mouse_mm10\n" \
      "python manage.py populate_db --disease loaded/disease.list\n" \
      "python manage.py populate_db --vcf file.vcf.gz --org human_GRCh38"
    
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
        make_option('--vcf',
            dest='vcf',
            help='VCF file of SNP features'),
        ) + (
        make_option('--chr',
            dest='chr',
            help='Chromosome sequence lengths'),
        )


    def _create_disease_cvterms(self, **options):
        
        dilList = []
        dilList.append(Cvterm(name='disease short name', definition=''))
        dilList.append(Cvterm(name='colour', definition=''))
        create_cvterms("DIL", "DIL terms", dilList)
        dil_cv = Cv.objects.get(name="DIL")

        # read disease list as two column tab delimited file
        f = open(options['disease'], 'r')
        for line in f:
            if(line.startswith("#")):
                continue
            termList = []
            parts = re.split('\t', line)
            termList.append(Cvterm(name=parts[0], definition=parts[1]))
            create_cvterms("disease", "disease types", termList)

            cv = Cv.objects.get(name="disease")
            cvterm = Cvterm.objects.get(cv=cv, name=parts[0])
            type = Cvterm.objects.get(cv=dil_cv, name='colour')
            Cvtermprop(cvterm=cvterm, type=type, value=parts[3].rstrip(), rank=0).save()
            type = Cvterm.objects.get(cv=dil_cv, name='disease short name')
            Cvtermprop(cvterm=cvterm, type=type, value=parts[2], rank=parts[4]).save()

                              

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


    def handle(self, *args, **options):
        if options['disease']:
          self._create_disease_cvterms(**options)
        elif options['bands']:
          bands = BandsManager()
          bands.create_bands(**options)
        elif options['gff']:
          gff = GFFManager()
          gff.create_gff_features(**options)
        elif options['vcf']:
          vcf = VCFManager()
          vcf.create_vcf_features(**options)
        elif options['chr']:
          self._create_chr_features(**options)
