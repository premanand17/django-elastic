from django.test import TestCase
from db.models import Feature, Cv, Cvterm, Organism, Db, Dbxref, FeatureDbxref
from django.core.urlresolvers import reverse
from django.template.base import Template
from django.template.context import Context


class GenesTestCase(TestCase):
    ''' Set up the data to test with. '''
    def setUp(self):
        ''' add a feature to the database '''
        cv = Cv.objects.create(name='sequence')
        db = Db.objects.create(name='null')
        dbxref = Dbxref.objects.create(db_id=db.db_id, accession='gene')
        termtype = Cvterm(dbxref_id=dbxref.dbxref_id, cv_id=cv.cv_id,
                          name='gene', definition='gene',
                          is_obsolete=0, is_relationshiptype=0)
        termtype.save()
        organism = Organism.objects.create(common_name='human_GRCh38')
        self.feature = Feature(organism=organism, name='9652',
                               uniquename='PTPN22',
                               type=termtype, is_analysis=0, is_obsolete=0)
        self.feature.save()
        ''' add a feature_dbxref '''
        db = Db.objects.create(name='Ensembl')
        dbxref = Dbxref.objects.create(db=db, accession='ENSG00000134242')
        FeatureDbxref.objects.create(dbxref=dbxref, feature=self.feature)

    ''' Test the gene page. '''
    def test_genes(self):
        resp = self.client.get(reverse('gene_page',
                                       kwargs={'gene': 'PTPN22'}))
        self.assertEqual(resp.status_code, 200)
        # check we've used the right template
        self.assertTemplateUsed(resp, 'gene/gene.html')

    ''' Test the show_gene_section tag. '''
    def test_inclusion_tag(self):
        t = Template('{% load gene_tags %}{% show_gene_section feature %}')
        context = {'feature': self.feature}
        c = Context(context)
        rendered = t.render(c)
        self.assertIn("PTPN22", rendered)
        self.assertIn("9652", rendered)
        self.assertIn("ENSG00000134242", rendered)
