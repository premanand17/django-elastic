from django.test import TestCase
from db.models import Feature, Cv, Cvterm, Organism, Db, Dbxref, FeatureDbxref
from django.core.urlresolvers import reverse
from django.template.base import Template
from django.template.context import Context


class GenesTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        ''' Set up the data to test with. '''
        ''' add a feature to the database '''
        super(GenesTestCase, cls).setUpClass()
        cv = Cv.objects.create(name='sequence')
        db = Db.objects.create(name='null')
        dbxref = Dbxref.objects.create(db_id=db.db_id, accession='gene')
        termtype = Cvterm(dbxref_id=dbxref.dbxref_id, cv_id=cv.cv_id,
                          name='gene', definition='gene',
                          is_obsolete=0, is_relationshiptype=0)
        termtype.save()
        organism = Organism.objects.create(common_name='human_GRCh38')
        cls.feature = Feature(organism=organism, name='9652',
                              uniquename='PTPN22',
                              type=termtype, is_analysis=0, is_obsolete=0)
        cls.feature.save()
        ''' add a feature_dbxref '''
        db = Db.objects.create(name='Ensembl')
        dbxref = Dbxref.objects.create(db=db, accession='ENSG00000134242')
        FeatureDbxref.objects.create(dbxref=dbxref, feature=cls.feature)

    def test_genes(self):
        ''' Test the gene page. '''
        resp = self.client.get(reverse('gene_page',
                                       kwargs={'gene': 'PTPN22'}))
        self.assertEqual(resp.status_code, 200)
        # check we've used the right template
        self.assertTemplateUsed(resp, 'gene/gene.html')

    def test_inclusion_tag1(self):
        ''' Test the show_gene_section tag. '''
        t = Template('{% load gene_tags %}{% show_gene_section feature %}')
        context = {'feature': self.feature}
        c = Context(context)
        rendered = t.render(c)
        self.assertIn("PTPN22", rendered)
        self.assertIn("9652", rendered)
        self.assertIn("ENSG00000134242", rendered)

    def test_inclusion_tag2(self):
        ''' Test the show_es_gene_section tag - given a gene symbol '''
        t = Template('{% load gene_tags %}' +
                     '{% show_es_gene_section gene_symbol=gene %}')
        context = {'gene': 'PTPN22'}
        c = Context(context)
        rendered = t.render(c)
        self.assertIn("PTPN22", rendered)
        self.assertIn("9652", rendered)
        self.assertIn("ENSG00000134242", rendered)

    def test_inclusion_tag3(self):
        ''' Test the show_es_gene_section tag - given a position
        on a sequence '''
        t = Template('{% load gene_tags %}' +
                     '{% show_es_gene_section seqid=seqid start_pos=pos %}')
        context = {'seqid': '1', 'pos': 113834947}
        c = Context(context)
        rendered = t.render(c)
        self.assertIn("PTPN22", rendered)
        self.assertIn("9652", rendered)
        self.assertIn("ENSG00000134242", rendered)

    def test_inclusion_tag4(self):
        ''' Test the show_es_gene_section tag - given a range
        on a sequence '''
        t = Template('{% load gene_tags %}' +
                     '{% show_es_gene_section seqid=seqid ' +
                     'start_pos=start_pos end_pos=end_pos%}')
        context = {'seqid': '1', 'start_pos': 2431888, 'end_pos': 2880054}
        c = Context(context)
        rendered = t.render(c)
        self.assertIn("PANK4", rendered)
