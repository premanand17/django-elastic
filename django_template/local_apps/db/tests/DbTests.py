from django.test import TestCase
from db.models import Cv

# models test
class CvTest(TestCase):

    def create_cv(self, name="test", definition="this is only a test"):
        return Cv.objects.create(name=name, definition=definition)

    def test_cv_creation(self):
        cv = self.create_cv()
        self.assertTrue(isinstance(cv, Cv))
        self.assertEqual(cv.__str__(), cv.name)

