# encoding=utf-8
import datetime
import os

from django.test import TestCase, SimpleTestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.db import IntegrityError

from apps.front import models
from apps.front import templatetags


### MODEL TESTS ###

class LecturerModelTest(TestCase):
    fixtures = ['testusers', 'testlecturer', 'testlratings']

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


class DocumentModelTest(TransactionTestCase):
    def setUp(self):
        self.john = User.objects.create_user('john', 'john@example.com', 'johnpasswd')
        self.marc = User.objects.create_user('marc', 'marc@example.com', 'marcpasswd')
        self.pete = User.objects.create_user('pete', 'pete@example.com', 'petepasswd')
        self.document = models.Document.objects.create(
                name='Analysis 1 Theoriesammlung',
                dtype=models.Document.DTypes.SUMMARY,
                description='Dieses Dokument ist eine Zusammenfassung der \
                    Theorie aus dem AnI1-Skript auf 8 Seiten. Das Dokument ist \
                    in LaTeX gesetzt, Source ist hier: http://j.mp/fjtleh - \
                    Gute Ergänzungen sind erwünscht!',
                uploader=self.john)
        self.document.DocumentRating.create(user=self.marc, rating=5)
        self.document.DocumentRating.create(user=self.pete, rating=2)

    def testBasicProperties(self):
        self.assertEqual(self.document.name, 'Analysis 1 Theoriesammlung')
        self.assertTrue(self.document.description.startswith('Dieses Dokument'))
        self.assertEqual(self.document.dtype, models.Document.DTypes.SUMMARY)
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

    def testNullValueUploader(self):
        d = models.Document()
        d.name = 'spam'
        d.description = 'ham'
        d.dtype = models.Document.DTypes.SUMMARY
        try:
            d.save()
        except IntegrityError:
            self.fail("A document with no uploader should not throw an IntegrityError.")


class QuoteModelTest(TestCase):
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
        self.assertTrue(q.date_available())

    def testNullValueAuthor(self):
        q = models.Quote()
        q.lecturer = models.Lecturer.objects.all()[0]
        q.quote = 'spam'
        q.comment = 'ham'
        try:
            q.save()
        except IntegrityError:
            self.fail("A quote with no author should not throw an IntegrityError.")

    def test1970Quote(self):
        """Check whether a quote from 1970-1-1 is marked as date_available=False."""
        q = models.Quote()
        q.lecturer = models.Lecturer.objects.all()[0]
        q.author = models.User.objects.all()[0]
        q.quote = 'spam'
        q.comment = 'ham'
        q.date = datetime.datetime(1970, 1, 1)
        self.assertFalse(q.date_available())


class UserModelTest(TransactionTestCase):
    def setUp(self):
        self.john = User.objects.create(username='john')
        self.marc = User.objects.create(username='marc', first_name=u'Marc')
        self.pete = User.objects.create(username='pete', last_name=u'Peterson')
        self.mike = User.objects.create(username='mike', first_name=u'Mike', last_name=u'Müller')

    def testName(self):
        """Test whether the custom name function returns the correct string."""
        self.assertEqual(self.john.name(), u'john')
        self.assertEqual(self.marc.name(), u'Marc')
        self.assertEqual(self.pete.name(), u'Peterson')
        self.assertEqual(self.mike.name(), u'Mike Müller')

    def testUserProfileCreation(self):
        """Test whether a user profile is created when a user is created."""
        u = User.objects.create_user("profiletester", "pt@example.com", "pwd")
        try:
            u.get_profile()
        except ObjectDoesNotExist:
            self.fail("Userprofile was not automatically created for a new user.")


class EventModelTest(TestCase):
    fixtures = ['testusers']
    
    def testDateTimeEvent(self):
        user = User.objects.get(username='testuser')
        event = models.Event.objects.create(
            summary='Testbar',
            description=u'This is a bar where people drink and party to \
                          test the studentenportal event feature.',
            author=user,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59))

        self.assertEqual(event.summary, 'Testbar')
        self.assertIsNone(event.end_date)
        self.assertEqual(event.author.username, 'testuser')
        self.assertTrue(event.is_over())
        self.assertIsNone(event.days_until())

    def testAllDayEvent(self):
        user = User.objects.get(username='testuser')
        start_date = datetime.date.today() + datetime.timedelta(days=365)
        event = models.Event.objects.create(
            summary='In a year',
            description='This happens in a year from now.',
            author=user,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=1))

        self.assertEqual(event.summary, 'In a year')
        self.assertIsNone(event.start_time)
        self.assertIsNone(event.end_time)
        self.assertFalse(event.is_over())
        self.assertTrue(event.all_day())
        self.assertEqual(event.days_until(), 365)

    def testNullValueAuthor(self):
        event = models.Event()
        event.summary='Testbar'
        event.description=u'Dies ist eine bar deren autor nicht mehr existiert.'
        event.author=None
        event.start_date=datetime.date(day=1, month=9, year=2010)
        event.start_time=datetime.time(hour=19, minute=30)
        event.end_time=datetime.time(hour=23, minute=59)
        try:
            event.save()
        except IntegrityError:
            self.fail("An event with no author should not throw an IntegrityError.")


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
    basepath = '/dokumente/an1i/'
    docurl1 = basepath + '1/'
    docurl2 = basepath + '2/'
    docurl3 = basepath + '3/'
    filepath1 = os.path.join(settings.MEDIA_ROOT, 'documents', 'Analysis-Theoriesammlung.pdf')
    filepath23 = os.path.join(settings.MEDIA_ROOT, 'documents', 'zf_mit_umlaut_6.doc')

    def setUp(self):
        self.file1_existed = os.path.exists(self.filepath1)
        self.file2_existed = os.path.exists(self.filepath23)
        if not self.file1_existed:
            open(self.filepath1, 'w').close()
        if not self.file2_existed:
            open(self.filepath23, 'w').close()

    def testSummaryServed(self):
        """Assert that the summaries get served, even without login."""
        response = self.client.get(self.docurl1)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.docurl2)
        self.assertEqual(response.status_code, 200)

    def testExamRequireLogin(self):
        """Assert that the exams require login."""
        response = self.client.get(self.docurl3)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.basepath)

    def testExamServed(self):
        """Assert that the exams get served when logged in."""
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.docurl3)
        self.assertEqual(response.status_code, 200)

    def testUmlautDocumentServed(self):
        """Test whether documents with umlauts in their original filename
        can be served."""
        response = self.client.get(self.docurl2)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        if not self.file1_existed:
            os.remove(self.filepath1)
        if not self.file2_existed:
            os.remove(self.filepath23)


class DocumentcategoryListViewTest(TestCase):
    fixtures = ['testdocs', 'testusers']
    taburl = '/dokumente/'

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, '<h1>Dokumente</h1>')

    def testModuleName(self):
        """Test whether the module An1I appears in the list."""
        response = self.client.get(self.taburl)
        self.assertContains(response, '<strong>An1I</strong>')
        self.assertContains(response, 'Analysis 1 für Informatiker')

    def testDocumentCount(self):
        """Test whether the downloadcount appears in the list."""
        response = self.client.get(self.taburl)
        self.assertContains(response, '<td>2</td>')

    def testUserAddButton(self):
        """Test whether the add button is shown when and only when the user is logged in."""
        response = self.client.get(self.taburl)
        self.assertNotContains(response, 'Modul hinzufügen')
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.taburl)
        self.assertContains(response, 'Modul hinzufügen')


class DocumentcategoryAddViewTest(TestCase):
    fixtures = ['testusers']
    taburl = '/dokumente/add/'

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
        self.assertRedirects(response1, '/dokumente/')
        response2 = self.client.get('/dokumente/prog2/')
        self.assertContains(response2, '<h1>Dokumente Prog2</h1>')


class DocumentListViewTest(TestCase):
    fixtures = ['testdocs', 'testusers']
    taburl = '/dokumente/an1i/'

    def setUp(self):
        self.response = self.client.get(self.taburl)

    def testTitle(self):
        self.assertContains(self.response, '<h1>Dokumente An1I</h1>')

    def testDocumentTitle(self):
        self.assertContains(self.response, '<h4><span class="label label-success">Zusammenfassung</span> Analysis 1 Theoriesammlung</h4>')

    def testUploaderName(self):
        self.assertContains(self.response, 'Another Guy')

    def testDescription(self):
        self.assertContains(self.response, 'Theorie aus dem AnI1-Skript auf 8 Seiten')

    def testUploadDate(self):
        self.assertContains(self.response, '18.12.2011')

    def testEditButtonLoggedOut(self):
        self.assertNotContains(self.response, 'href="/dokumente/an1i/1/edit/"')
        self.assertNotContains(self.response, 'href="/dokumente/an1i/2/edit/"')

    def testEditButtonLoggedIn(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.taburl)
        self.assertContains(response, 'href="/dokumente/an1i/1/edit/"')
        self.assertNotContains(response, 'href="/dokumente/an1i/2/edit/"')

    def testDeleteButtonLoggedOut(self):
        self.assertNotContains(self.response, 'href="/dokumente/an1i/1/delete/"')
        self.assertNotContains(self.response, 'href="/dokumente/an1i/2/delete/"')

    def testDeleteButtonLoggedIn(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.taburl)
        self.assertContains(response, 'href="/dokumente/an1i/1/delete/"')
        self.assertNotContains(response, 'href="/dokumente/an1i/2/delete/"')

    def testDownloadCount(self):
        filepath = os.path.join(settings.MEDIA_ROOT, 'documents', 'Analysis-Theoriesammlung.pdf')
        file_existed = os.path.exists(filepath)
        if not file_existed:
            open(filepath, 'w').close()
        response0 = self.client.get(self.taburl)
        self.assertContains(response0, '<p>0 Downloads</p>')
        self.client.get(self.taburl + '1/')
        response1 = self.client.get(self.taburl)
        self.assertContains(response1, '<p>1 Download</p>')
        self.client.get(self.taburl + '1/')
        response2 = self.client.get(self.taburl)
        self.assertContains(response2, '<p>2 Downloads</p>')
        if not file_existed:
            os.remove(filepath)

    def testNullValueUploader(self):
        """Test whether a document without an uploader does not raise an error."""
        models.DocumentCategory.objects.create(
            id=123, name='test', description='spam ham bacon')
        models.Document.objects.create(
            name='Analysis 1 Theoriesammlung',
            description='Dieses Dokument ist eine Zusammenfassung der \
                Theorie aus dem AnI1-Skript auf 8 Seiten. Das Dokument ist \
                in LaTeX gesetzt, Source ist hier: http://j.mp/fjtleh - \
                Gute Ergänzungen sind erwünscht!',
            document='zf.pdf',
            dtype=models.Document.DTypes.SUMMARY,
            original_filename='zf.pdf',
            category_id=123,
            uploader=None)
        response = self.client.get('/dokumente/test/')
        self.assertContains(response, 'Analysis 1 Theoriesammlung')
        self.assertContains(response, 'Dieses Dokument ist eine Zusammenfassung der')


class EventsViewTest(TestCase):
    taburl = '/events/'

    def setUp(self):
        self.response = self.client.get(self.taburl)

    def testTitle(self):
        self.assertContains(self.response, '<h1>Events</h1>')

    def testContent(self):
        self.assertContains(self.response, '<h2>Kommende Veranstaltungen</h2>')
        self.assertContains(self.response, '<h2>Vergangene Veranstaltungen</h2>')

    def testNullAuthor(self):
        models.Event.objects.create(
            summary='Testbar',
            description=u'This is a bar where people drink and party to \
                          test the studentenportal event feature.',
            author=None,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59))
        response = self.client.get(self.taburl)
        self.assertEqual(response.status_code, 200)


class EventDetailViewTest(TestCase):
    fixtures = ['testusers']

    def setUp(self):
        self.user = models.User.objects.get(pk=1)
        self.event = models.Event.objects.create(
            id=1,
            summary='Testbar',
            description=u'This is a bar where people drink and party to \
                          test the studentenportal event feature.',
            author=self.user,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59))

    def tearDown(self):
        self.event.delete()

    def testTitle(self):
        response = self.client.get('/events/1/')
        self.assertContains(response, '<h1>Testbar</h1>')

    def testContent(self):
        response = self.client.get('/events/1/')
        self.assertContains(response, '<p>This is a bar where people drink and party \
                        to test the studentenportal event feature.</p>', html=True)
        self.assertContains(response, '<strong>Start:</strong>')
        self.assertContains(response, '1. September 2010 19:30')
        self.assertContains(response, '<strong>Ende:</strong>')
        self.assertContains(response, '1. September 2010 23:59')


class QuoteAddViewTest(TestCase):
    fixtures = ['testusers', 'testlecturer']

    def setUp(self):
        self.client.login(username='testuser', password='test')

    def testGenericForm(self):
        """Test the form that is shown if no lecturer is preselected."""
        response = self.client.get('/zitate/add/')
        self.assertContains(response, '<h1>Zitat hinzufügen</h1>')
        self.assertContains(response, '<option value="" selected="selected">---------</option>')

    def testPrefilledForm(self):
        """Test the form that is shown if a lecturer is preselected."""
        response = self.client.get('/zitate/1/add/')
        self.assertContains(response, '<h1>Zitat hinzufügen</h1>')
        self.assertContains(response, '<select name="lecturer" id="id_lecturer">')
        self.assertContains(response, '<option value="1" selected="selected">Krakaduku David</option>')

    def testFormSubmission(self):
        """Test whether a quote submission gets saved correctly."""
        response = self.client.post('/zitate/add/', {
            'lecturer': '1',
            'quote': 'ich bin der beste dozent von allen.',
            'comment': 'etwas arrogant, nicht?',
        })
        self.assertRedirects(response, '/zitate/')
        response2 = self.client.get('/zitate/')
        self.assertContains(response2, '<td>ich bin der beste dozent von allen.</td>')
        self.assertContains(response2, '<td>etwas arrogant, nicht?</td>')


class QuoteViewTest(TestCase):
    fixtures = ['testusers', 'testlecturer']

    def setUp(self):
        self.client.login(username='testuser', password='test')
        self.response = self.client.get('/zitate/')

    def testTitle(self):
        self.assertContains(self.response, '<h1>Zitate</h1>')

    def testQuoteInList(self):
        """Test whether an added quote shows up in the list."""
        models.Quote.objects.create(
            lecturer=models.Lecturer.objects.all()[0],
            author_id=1,
            quote='spam',
            comment='ham')
        response = self.client.get('/zitate/')
        self.assertContains(response, 'spam')
        self.assertContains(response, 'ham')

    def testNullValueAuthor(self):
        """Test whether a quote without an author does not raise an error."""
        models.Quote.objects.create(
            lecturer=models.Lecturer.objects.all()[0],
            quote='spam',
            comment='ham')
        response = self.client.get('/zitate/')
        self.assertContains(response, 'spam')
        self.assertContains(response, 'ham')



class LoginTest(TestCase):
    fixtures = ['testusers']
    url = '/accounts/login/'

    def testTitle(self):
        r = self.client.get(self.url)
        self.assertContains(r, '<h1>Login</h1>')

    def testLogin(self):
        r1 = self.client.get('/zitate/')
        self.assertEqual(r1.status_code, 302)
        self.client.login(username='testuser', password='test')
        r2 = self.client.get('/zitate/')
        self.assertEqual(r2.status_code, 200)

    def testCaseInsensitveLogin(self):
        r1 = self.client.post(self.url, {'username': 'testuser', 'password': 'test'})
        self.assertEqual(r1.status_code, 302)
        r2 = self.client.post(self.url, {'username': 'Testuser', 'password': 'test'})
        self.assertEqual(r2.status_code, 302)


class RegistrationViewTest(TestCase):
    registration_url = '/accounts/register/'

    def testRegistrationPage(self):
        response = self.client.get(self.registration_url)
        self.assertContains(response, '<h1>Registrieren</h1>')
        self.assertContains(response, 'Diese Registrierung ist Personen mit einer HSR-Email-Adresse vorbehalten')
        self.assertContains(response, '<form')

    def testRegistration(self):
        """Test that a registration is successful and that an activation email
        is sent."""
        response = self.client.post(self.registration_url, {
            'username': 'testuser',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        self.assertRedirects(response, '/accounts/register/complete/')
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[studentenportal.ch] Aktivierung')


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


class StatsViewTest(TestCase):
    fixtures = ['testusers', 'testlecturer', 'testlratings']
    taburl = '/statistiken/'

    def testLoginRequired(self):
        response = self.client.get(self.taburl)
        self.assertRedirects(response, '/accounts/login/?next=/statistiken/')

    def testTitle(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.taburl)
        self.assertContains(response, '<h1>Statistiken</h1>')


### TEMPLATETAG TESTS ###

class GetRangeTest(SimpleTestCase):
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


class GetRange1Test(SimpleTestCase):
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
