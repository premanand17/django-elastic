from django.test import TestCase
from db.models import Feature, Cv, Cvterm, Organism, Db, Dbxref
from django.core.urlresolvers import reverse


class GenesTestCase(TestCase):

    def setUp(self):
        cv = Cv.objects.create(name='sequence')
        db = Db.objects.create(name='null')
        dbxref = Dbxref.objects.create(db_id=db.db_id, accession='gene')
        termtype = Cvterm(dbxref_id=dbxref.dbxref_id, cv_id=cv.cv_id,
                          name='gene', definition='gene',
                          is_obsolete=0, is_relationshiptype=0)
        termtype.save()
        organism = Organism.objects.create(common_name='human_GRCh38')
        self.feature = Feature(organism=organism, name='PTPN22',
                               uniquename='PTPN22',
                               type=termtype, is_analysis=0, is_obsolete=0)
        self.feature.save()

    def test_genes(self):
        resp = self.client.get(reverse('gene_page',
                                       kwargs={'gene': 'PTPN22'}))
        self.assertEqual(resp.status_code, 200)
        # check we've used the right template
        self.assertTemplateUsed(resp, 'gene/gene.html')
