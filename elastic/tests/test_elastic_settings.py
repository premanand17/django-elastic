from django.test import TestCase
from elastic.elastic_settings import ElasticSettings
from elastic.exceptions import SettingsError
from django.test.utils import override_settings
from elastic.tests.settings_idx import OVERRIDE_SETTINGS3


@override_settings(ELASTIC=OVERRIDE_SETTINGS3)
class ElasticSettingsTest(TestCase):

    def test_get_label(self):
        self.assertRaises(SettingsError, ElasticSettings.get_label, 'ABC')
        self.assertTrue(isinstance(ElasticSettings.get_label('MARKER', idx_type='MARKER', label='description'), str))
        self.assertTrue(isinstance(ElasticSettings.get_label('MARKER'), str))
