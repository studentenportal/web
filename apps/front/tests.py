# encoding=utf-8
import datetime
import os

from django.test import TestCase
from django.utils import unittest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import IntegrityError

from apps.front import models
from apps.front import templatetags


### MODEL TESTS ###

class LecturerModelTest(TestCase):
    fixtures = ['testlecturer', 'testlratings']

    def setUp(self):
        self.lecturer = models.Lecturer.objects.get()

    def testRatings(self):
        """Test whether ratings are calculated correctly."""
        self.assertEqual(self.lecturer.avg_rating_d(), 7)
        self.assertEqual(self.lecturer.avg_rating_m(), 10)
        self.assertEqual(self.lecturer.avg_rating_f(), 0)

    def testName(self):
        self.assertEqual(self.lecturer.name(), 'Prof. Dr. Krakaduku David')


class LecturerRatingModelTest(TestCase):
    fixtures = ['testusers', 'testlecturer']

    def tearDown(self):
        for rating in models.LecturerRating.objects.all():
            rating.delete()

    def create_default_rating(self, category=u'd', rating=5):
        """Helper function to create a default rating."""
        user = models.User.objects.all()[0]
        lecturer = models.Lecturer.objects.get()
        lr = models.LecturerRating(
            user=user,
            lecturer=lecturer,
            category=category,
            rating=rating)
        lr.full_clean()
        lr.save()

    def testAddSimpleRating(self):
        """Test whether a simple valid rating can be added."""
        self.create_default_rating()
        self.assertEqual(models.LecturerRating.objects.count(), 1)

    def testAddInvalidCategory(self):
        """Test whether only a valid category can be added."""
        with self.assertRaises(ValidationError):
            self.create_default_rating(category=u'x')

    def testAddInvalidRating(self):
        """Test whether invalid ratings raise validation errors."""
        with self.assertRaises(ValidationError):
            self.create_default_rating(rating=11)
        with self.assertRaises(ValidationError):
            self.create_default_rating(rating=0)

    def testUniqueTogether(self):
        """Test the unique_together constraint."""
        self.create_default_rating()
        with self.assertRaises(ValidationError):
            self.create_default_rating(rating=6)


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
        """Test the document rating average calculation."""
        self.assertEqual(self.document.DocumentRating.count(), 2)
        self.assertEqual(self.document.rating(), 4)
        self.assertEqual(self.document.rating_exact(), 3.5)

    def testRatingValidation(self):
        dr = models.DocumentRating.objects.get(document=self.document, user=self.marc)
        dr.rating = 11
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


class QuoteModelTst(TestCase):
    fixtures = ['testusers', 'testlecturer']

    def testQuote(self):
        quote = "Dies ist ein längeres Zitat, das dazu dient, zu testen " + \
            "ob man Zitate erfassen kann und ob die Länge des Zitats mehr " + \
            "als 255 Zeichen enthalten darf. Damit kann man sicherstellen, " + \
            "dass im Model kein CharField verwendet wurde. Denn wir wollen " + \
            "ja nicht, dass längere Zitate hier keinen Platz haben :)"
        before = datetime.datetime.now()
        q = models.Quote()
        q.author = models.User.objects.all()[0]
        q.lecturer = models.Lecturer.objects.all()[0]
        q.quote = quote
        q.comment = "Eine Bemerkung zum Kommentar"
        q.save()
        after = datetime.datetime.now()
        self.assertTrue(before < q.date < after)


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


class LecturerListViewTest(TestCase):
    fixtures = ['testusers', 'testlecturer']

    def testLoginRequired(self):
        response = self.client.get('/dozenten/')
        self.assertRedirects(response, '/accounts/login/?next=/dozenten/')

    def testContent(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get('/dozenten/k/')
        self.assertContains(response, '<h1>Unsere Dozenten</h1>')
        self.assertContains(response, 'Prof. Dr. Krakaduku David')


class LecturerDetailViewTest(TestCase):
    fixtures = ['testusers', 'testlecturer']
    url = '/dozenten/1/'

    def testLoginRequired(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.url)

    def testDescription(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertContains(response, '<h1>Prof. Dr. Krakaduku David</h1>')
        self.assertContains(response, 'San Diego')
        self.assertContains(response, 'Quantenphysik, Mathematik für Mathematiker')

    def testContact(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertContains(response, '1.337')
        self.assertContains(response, 'krakaduku@hsr.ch')


class ProfileViewTest(TestCase):
    def testUnauthRedirect(self):
        response = self.client.get('/profil/')
        self.assertEqual(response.status_code, 302)


class DocumentDownloadTest(TestCase):
    fixtures = ['testdocs', 'testusers']
    docurl = '/zusammenfassungen/an1i/1/'
    filepath = os.path.join(settings.MEDIA_ROOT, 'documents', 'Analysis-Theoriesammlung.pdf')

    def setUp(self):
        self.file_existed = os.path.exists(self.filepath)
        if not self.file_existed:
            open(self.filepath, 'w').close()

    def testLoginRequired(self):
        response = self.client.get(self.docurl)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.docurl)

    def testDocumentServed(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.docurl)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        if not self.file_existed:
            os.remove(self.filepath)


class DocumentcategoryListViewTest(TestCase):
    fixtures = ['testdocs', 'testusers']
    taburl = '/zusammenfassungen/'

    def setUp(self):
        self.client.login(username='testuser', password='test')

    def testLoginRequired(self):
        self.client.logout()
        response = self.client.get(self.taburl)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.taburl)

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, '<h1>Zusammenfassungen</h1>')

    def testModuleName(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, '<strong>An1I</strong>')
        self.assertContains(response, 'Analysis 1 für Informatiker')

    def testDocumentCount(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, '<td>2</td>')

    def testUserAddButton(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.taburl)
        self.assertContains(response, 'Modul hinzufügen')


class DocumentcategoryAddViewTest(TestCase):
    fixtures = ['testusers']
    taburl = '/zusammenfassungen/add/'

    def setUp(self):
        self.client.login(username='testuser', password='test')

    def testLoginRequired(self):
        self.client.logout()
        response = self.client.get(self.taburl)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.taburl)

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, 'Modul hinzufügen')

    def testAdd(self):
        data = {
            'name': 'Prog2',
            'description': 'Programmieren 2',
        }
        response1 = self.client.post(self.taburl, data)
        self.assertRedirects(response1, '/zusammenfassungen/')
        response2 = self.client.get('/zusammenfassungen/prog2/')
        self.assertContains(response2, '<h1>Zusammenfassungen Prog2</h1>')


class DocumentListView(TestCase):
    fixtures = ['testdocs', 'testusers']
    taburl = '/zusammenfassungen/an1i/'

    def setUp(self):
        self.client.login(username='testuser', password='test')
        self.response = self.client.get(self.taburl)

    def testTitle(self):
        self.assertContains(self.response, '<h1>Zusammenfassungen An1I</h1>')

    def testDocumentTitle(self):
        self.assertContains(self.response, '<h4>Analysis 1 Theoriesammlung</h4>')

    def testUploaderName(self):
        self.assertContains(self.response, 'Another Guy')

    def testDescription(self):
        self.assertContains(self.response, 'Theorie aus dem AnI1-Skript auf 8 Seiten')

    def testUploadDate(self):
        self.assertContains(self.response, '18.12.2011')

    def testEditButton(self):
        self.assertContains(self.response, 'href="/zusammenfassungen/an1i/1/edit/"')
        self.assertNotContains(self.response, 'href="/zusammenfassungen/an1i/2/edit/"')

    def testDeleteButton(self):
        self.assertContains(self.response, 'href="/zusammenfassungen/an1i/1/delete/"')
        self.assertNotContains(self.response, 'href="/zusammenfassungen/an1i/2/delete/"')

    def testDownloadCount(self):
        response_before = self.client.get(self.taburl)
        self.assertContains(response_before, '0 Downloads')
        self.client.get(self.taburl + '1/')
        self.client.get(self.taburl + '1/')
        response_after = self.client.get(self.taburl)
        self.assertContains(response_after, '2 Downloads')


class EventsViewTest(TestCase):
    taburl = '/events/'

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, '<h1>Events</h1>')


class LoginTest(TestCase):
    url = '/accounts/login/'

    def testTitle(self):
        r = self.client.get(self.url)
        self.assertContains(r, '<h1>Login</h1>')


class UserViewTest(TestCase):
    fixtures = ['testusers']

    def setUp(self):
        self.client.login(username='testuser', password='test')

    def testOwnUserView(self):
        response = self.client.get('/users/1/testuser/')
        self.assertContains(response, '<h1>testuser</h1>')
        self.assertContains(response, 'django-test@studentenportal.ch')

    def testOtherUserView(self):
        response = self.client.get('/users/2/testuser2/')
        self.assertContains(response, '<h1>Another Guy</h1>')
        self.assertContains(response, 'django-test2@studentenportal.ch')


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
