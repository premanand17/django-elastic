from django.test import TestCase
from django.core.management import call_command
import string
import random
from db.models import Cv, Db


class BandsViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        ''' Load fixture for all test methods in this class '''
        super(BandsViewsTestCase, cls).setUpClass()
        call_command('loaddata', 'cv.json', 'db.json', 'feature.json', verbosity=0)

    @classmethod
    def tearDownClass(cls):
        super(BandsViewsTestCase, cls).tearDownClass()
        # call_command('flush', verbosity=0, interactive=False)
        # flush command does not clear data presumably because the
        # models are managed
        Cv.objects.all().delete()
        Db.objects.all().delete()

    def test_band(self):
        ''' Test the home page '''
        self._home_page(self.client.get('/'))

    def test_band_uncached(self):
        ''' Test the home page '''
        self._home_page(self.client.get('/?'+self._id_generator()))

    def _home_page(self, resp):
        self.assertEqual(resp.status_code, 200)
        if resp.context is not None:  # if none it is cached
            self.assertEqual(resp.context['org'], 'human_GRCh38')
            self.assertTrue('srcfeatures' in resp.context)
            feature = resp.context['srcfeatures'][0]
            self.assertTrue(hasattr(feature, 'uniquename'))

    def test_cv(self):
        resp = self.client.get('/cvlist/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('cv_list' in resp.context)
        cv = resp.context['cv_list'][2]
        self.assertTrue(hasattr(cv, 'cv_id'))
        self.assertTrue(hasattr(cv, 'name'))

    def test_not_found(self):
        resp = self.client.get('/xxx/')
        self.assertEqual(resp.status_code, 404)

    def _id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
