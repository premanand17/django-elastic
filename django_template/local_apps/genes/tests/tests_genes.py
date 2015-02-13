from django.test import TestCase


class GenesTestCase(TestCase):

    def test_genes(self):
        resp = self.client.get('/genes/PTPN22/')
        self.assertEqual(resp.status_code, 200)
