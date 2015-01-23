from django.test import TestCase

class BandsViewsTestCase(TestCase):
    """Load fixture"""
    fixtures = ['db2.json']

    def test_band(self):
        resp = self.client.get('/human_GRCh38/')
        self.assertEqual(resp.status_code, 200)

        if resp.context is not None:  # if none it is cached
            #print(resp.context['srcfeatures'])
            self.assertEqual(resp.context['org'], 'human_GRCh38')
            self.assertTrue('srcfeatures' in resp.context)
            feature = resp.context['srcfeatures'][0]
            self.assertTrue(hasattr(feature, 'uniquename'))


    def test_cv(self):
        resp = self.client.get('/cvlist/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('cv_list' in resp.context)
        cv = resp.context['cv_list'][0]
        self.assertTrue(hasattr(cv, 'cv_id'))
        self.assertTrue(hasattr(cv, 'name'))
        
    def test_not_found(self):
        resp = self.client.get('/xxx/')
        self.assertEqual(resp.status_code, 404)

            