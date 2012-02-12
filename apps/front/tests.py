# encoding=utf8
import datetime

from django.test import TestCase
from django.utils import unittest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.front import models
from apps.front import templatetags


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
        self.assertTrue(isinstance(self.document.upload_date, datetime.datetime))

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


class UserModelTest(unittest.TestCase):
    def setUp(self):
        self.john = User.objects.create(username='john')
        self.marc = User.objects.create(username='marc', first_name=u'Marc')
        self.pete = User.objects.create(username='pete', last_name=u'Peterson')
        self.mike = User.objects.create(username='mike', first_name=u'Mike', last_name=u'Müller')

    def tearDown(self):
        self.john.delete()
        self.marc.delete()
        self.pete.delete()
        self.mike.delete()

    def testName(self):
        """Test whether the custom name function returns the correct string."""
        self.assertEqual(self.john.name(), u'john')
        self.assertEqual(self.marc.name(), u'Marc')
        self.assertEqual(self.pete.name(), u'Peterson')
        self.assertEqual(self.mike.name(), u'Mike Müller')


class EventModelTest(unittest.TestCase):
    def setUp(self):
        self.mike = User.objects.create(username='mike', first_name=u'Mike', last_name=u'Müller')

    def tearDown(self):
        self.mike.delete()

    def testDateTimeEvent(self):
        event = models.Event.objects.create(
            summary='Testbar',
            description=u'This is a bar where people drink and party to \
                          test the studentenportal event feature.',
            author=self.mike,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59))

        self.assertEqual(event.summary, 'Testbar')
        self.assertIsNone(event.end_date)
        self.assertEqual(event.author.username, 'mike')
        self.assertTrue(event.is_over())
        self.assertIsNone(event.days_until())

    def testAllDayEvent(self):
        start_date = datetime.date.today() + datetime.timedelta(days=365)
        event = models.Event.objects.create(
            summary='In a year',
            description='This happens in a year from now.',
            author=self.mike,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=1))

        self.assertEqual(event.summary, 'In a year')
        self.assertIsNone(event.start_time)
        self.assertIsNone(event.end_time)
        self.assertFalse(event.is_over())
        self.assertTrue(event.all_day())
        self.assertEqual(event.days_until(), 365)


### VIEW TESTS ###

class HomeViewTest(TestCase):
    def testHTTP200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class LecturersViewTest(TestCase):
    fixtures = ['testuser']

    def testLoginRequired(self):
        response = self.client.get('/dozenten/')
        self.assertRedirects(response, '/accounts/login/?next=/dozenten/')

    def testTitle(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get('/dozenten/')
        self.assertIn('<h2>Unsere Dozenten</h2>', response.content)


class ProfileViewTest(TestCase):
    def testUnauthRedirect(self):
        response = self.client.get('/profil/')
        self.assertEqual(response.status_code, 302)


class DocumentsViewTest(TestCase):
    taburl = '/zusammenfassungen/'

    def testHTTP200(self):
        response = self.client.get(self.taburl)
        self.assertEqual(response.status_code, 200)

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertIn('<h2>Zusammenfassungen</h2>', response.content)


class EventsViewTest(TestCase):
    taburl = '/events/'

    def testHTTP200(self):
        response = self.client.get(self.taburl)
        self.assertEqual(response.status_code, 200)

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertIn('<h2>Events</h2>', response.content)


class LoginTest(TestCase):
    url = '/accounts/login/'

    def testTitle(self):
        r = self.client.get(self.url)
        self.assertContains(r, '<h1>Login</h1>')

# TODO registration test


### TEMPLATETAG TESTS ###

class GetRangeTest(unittest.TestCase):
    def testZero(self):
        r = templatetags.tags.get_range(0)
        self.assertEqual(len(r), 0) 

    def testNegative(self):
        r = templatetags.tags.get_range(-5)
        self.assertEqual(len(r), 0)

    def testPositive(self):
        r = templatetags.tags.get_range(5)
        self.assertEqual(len(r), 5)
        self.assertEqual(r[0], 0)
        self.assertEqual(r[4], 4)


class GetRange1Test(unittest.TestCase):
    def testZero(self):
        r = templatetags.tags.get_range1(0)
        self.assertEqual(len(r), 0)

    def testOne(self):
        r = templatetags.tags.get_range1(1)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], 1)

    def testNegative(self):
        r = templatetags.tags.get_range1(-5)
        self.assertEqual(len(r), 0)

    def testPositive(self):
        r = templatetags.tags.get_range1(5)
        self.assertEqual(len(r), 5)
        self.assertEqual(r[0], 1)
        self.assertEqual(r[4], 5)
