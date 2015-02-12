from django.test import TestCase


class GenesTestCase(TestCase):
    """Load fixture"""
    fixtures = ['db2.json']

    def test_genes(self):
        resp = self.client.get('/genes/PTPN22/')
        self.assertEqual(resp.status_code, 200)
