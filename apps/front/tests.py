from django.utils import unittest
from django.test.client import Client

from apps.front.models import Lecturer


class LecturerTestCase(unittest.TestCase):
    def setUp(self):
        self.lecturer = Lecturer.objects.create(
                name='Jussuf Jolder',
                abbreviation='jol',
                subjects='Testsubject',
                description='Some guy')

    def testValidRatingsRange(self):
        """Rating must be between 1 and 6."""
        self.assertTrue(1.0 <= self.lecturer.avg_rating_d() <= 6.0)
        self.assertTrue(1.0 <= self.lecturer.avg_rating_m() <= 6.0)
        self.assertTrue(1.0 <= self.lecturer.avg_rating_f() <= 6.0)


class HomeViewTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Client()

    def testHTTP200(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)


class LecturersViewTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Client()

    def testHTTP200(self):
        response = self.c.get('/dozenten/')
        self.assertEqual(response.status_code, 200)

    def testTitle(self):
        response = self.c.get('/dozenten/')
        self.assertIn('<h2>Unsere Dozenten</h2>', response.content)


class ProfileViewTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Client()

    def testUnauthRedirect(self):
        response = self.c.get('/profil/')
        self.assertEqual(response.status_code, 302)


class DocumentsViewTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Client()
        self.taburl = '/zusammenfassungen/'

    def testHTTP200(self):
        response = self.c.get(self.taburl)
        self.assertEqual(response.status_code, 200)

    def testTitle(self):
        response = self.c.get(self.taburl)
        self.assertIn('<h2>Zusammenfassungen</h2>', response.content)
