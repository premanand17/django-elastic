from django.test import TestCase
from django.core.urlresolvers import reverse


class MarkerTestCase(TestCase):

    def test_marker(self):
        ''' Test the marker page. '''
        resp = self.client.get(reverse('marker_page',
                                       kwargs={'marker': 'rs2476601'}))
        self.assertEqual(resp.status_code, 200)
        # check we've used the right template
        self.assertTemplateUsed(resp, 'marker/marker.html')
