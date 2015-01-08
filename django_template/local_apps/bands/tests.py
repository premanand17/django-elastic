from django.test import TestCase

class BandsViewsTestCase(TestCase):
    """Load fixture"""
    fixtures = ['db2.json']

    def test_index(self):
        resp = self.client.get('/bands/cached/human_GRCh38/')
        self.assertEqual(resp.status_code, 200)


