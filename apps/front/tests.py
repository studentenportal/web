# encoding=utf8
from datetime import datetime

from django.utils import unittest
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.front import models


### MODEL TESTS ###

class LecturerModelTest(unittest.TestCase):
    def setUp(self):
        self.lecturer = models.Lecturer.objects.create(
                name='Jussuf Jolder',
                abbreviation='jol',
                subjects='Testsubject',
                description='Some guy')

    def tearDown(self):
        self.lecturer.delete()

    def testValidRatingsRange(self):
        """Rating must be between 1 and 6."""
        self.assertTrue(1.0 <= self.lecturer.avg_rating_d() <= 6.0)
        self.assertTrue(1.0 <= self.lecturer.avg_rating_m() <= 6.0)
        self.assertTrue(1.0 <= self.lecturer.avg_rating_f() <= 6.0)


class DocumentModelTest(unittest.TestCase):
    def setUp(self):
        self.john = User.objects.create_user('john', 'john@example.com', 'johnpasswd')
        self.marc = User.objects.create_user('marc', 'marc@example.com', 'marcpasswd')
        self.pete = User.objects.create_user('pete', 'pete@example.com', 'petepasswd')
        self.document = models.Document.objects.create(
                name='Analysis 1 Theoriesammlung',
                description='Dieses Dokument ist eine Zusammenfassung der \
                    Theorie aus dem AnI1-Skript auf 8 Seiten. Das Dokument ist \
                    in LaTeX gesetzt, Source ist hier: http://j.mp/fjtleh - \
                    Gute Ergänzungen sind erwünscht!',
                uploader=self.john)
        self.document.DocumentRating.create(user=self.marc, rating=5)
        self.document.DocumentRating.create(user=self.pete, rating=2)

    def tearDown(self):
        # Remove all created objects
        self.john.delete()
        self.marc.delete()
        self.pete.delete()
        self.document.delete()

    def testBasicProperties(self):
        self.assertEqual(self.document.name, 'Analysis 1 Theoriesammlung')
        self.assertTrue(self.document.description.startswith('Dieses Dokument'))
        self.assertTrue(isinstance(self.document.uploader, User))

    def testUploadDate(self):
        """Check whether upload date has been set."""
        self.assertTrue(isinstance(self.document.upload_date, datetime))

    def testRatingAverage(self):
        self.assertEqual(self.document.DocumentRating.count(), 2)
        self.assertEqual(self.document.rating(), 4)
        self.assertEqual(self.document.rating_exact(), 3.5)

    def testRatingValidation(self):
        dr = models.DocumentRating.objects.get(document=self.document, user=self.marc)
        dr.rating = 6
        self.assertRaises(ValidationError, dr.full_clean)
        dr.rating = 0
        self.assertRaises(ValidationError, dr.full_clean)

    def testRatingAuthorValidation(self):
        """A user may not rate his own uploads."""
        dr = models.DocumentRating(document=self.document, user=self.john)
        self.assertRaises(ValidationError, dr.full_clean)

    def testDuplicateRatingsValidation(self):
        """A user cannot rate the same document twice."""
        dr = models.DocumentRating(document=self.document, user=self.marc)
        self.assertRaises(IntegrityError, dr.save)


### VIEW TESTS ###

class HomeViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def testHTTP200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class LecturersViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def testHTTP200(self):
        response = self.client.get('/dozenten/')
        self.assertEqual(response.status_code, 200)

    def testTitle(self):
        response = self.client.get('/dozenten/')
        self.assertIn('<h2>Unsere Dozenten</h2>', response.content)


class ProfileViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def testUnauthRedirect(self):
        response = self.client.get('/profil/')
        self.assertEqual(response.status_code, 302)


class DocumentsViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.taburl = '/zusammenfassungen/'

    def testHTTP200(self):
        response = self.client.get(self.taburl)
        self.assertEqual(response.status_code, 200)

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertIn('<h2>Zusammenfassungen</h2>', response.content)
