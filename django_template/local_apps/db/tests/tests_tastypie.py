from tastypie.test import ResourceTestCase
from db.models import Cvterm, Cv, Db, Dbxref


class TastypieTest(ResourceTestCase):

    def setUp(self):
        super(TastypieTest, self).setUp()

        # Create a cv
        self.cv = Cv.objects.create(cv_id=12, name='local_test', definition='local definition - test')
        self.db = Db.objects.create(db_id=1, name='test')
        self.dbxref = Dbxref.objects.create(dbxref_id=1, db_id=1, accession='XXX')
        self.cvterm = Cvterm.objects.create(cvterm_id=12, dbxref_id=1, cv_id=12, name='test cvterm', is_obsolete=0, is_relationshiptype=0)
        #Cv(cv_id=12, name='local_test', definition='local definition - test').save()

    def test_get_list_unauthorzied(self):
        resp = self.api_client.get('/api/dev/cv/', format='json')
        self.assertValidJSONResponse(resp)

    def test_get_list_cvterms_unauthorzied(self):
        resp = self.api_client.get('/api/dev/cvterm/', format='json', cv='12')
        self.assertValidJSONResponse(resp)

