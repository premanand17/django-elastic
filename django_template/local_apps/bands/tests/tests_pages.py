from django.test import TestCase
from django.test.utils import setup_test_environment


class BandsViewsTestCase(TestCase):
    """Load fixture"""
    fixtures = ['db2.json']
    setup_test_environment()

    def test_index(self):
        resp = self.client.get('/bands/cached/human_GRCh38/')
        self.assertEqual(resp.status_code, 200)

        if resp.context is not None:  # if none it is cached
            #print(resp.context['srcfeatures'])
            self.assertEqual(resp.context['org'], 'human_GRCh38')
            self.assertTrue('srcfeatures' in resp.context)
            feature = resp.context['srcfeatures'][0]
            self.assertTrue(hasattr(feature, 'uniquename'))


