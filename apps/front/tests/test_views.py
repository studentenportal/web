# -*- coding: utf-8 -*-
import datetime
import os

from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.conf import settings

from BeautifulSoup import BeautifulSoup

from apps.front import models, forms


User = get_user_model()


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
        response = self.client.get('/dozenten/')
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
        self.assertContains(response, '<h1 class="lecturer-name" data-lecturer-pk="1">Prof. Dr. Krakaduku David</h1>')
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

    def setUp(self):
        self.response = self.client.get(self.taburl)

    def testTitle(self):
        self.assertContains(self.response, '<h1>Dokumente</h1>')

    def testModuleName(self):
        """Test whether the module An1I appears in the list."""
        self.assertContains(self.response, '<strong>An1I</strong>')
        self.assertContains(self.response, 'Analysis 1 für Informatiker')

    def testUserAddButton(self):
        """Test whether the add button is shown when and only when the user is logged in."""
        response1 = self.client.get(self.taburl)
        self.assertNotContains(response1, 'Modul hinzufügen')
        self.client.login(username='testuser', password='test')
        response2 = self.client.get(self.taburl)
        self.assertContains(response2, 'Modul hinzufügen')

    def testCounts(self):
        """Test whether the category counts are correct."""
        self.assertContains(self.response, '<td class="summary_count">2</td>')
        self.assertContains(self.response, '<td class="exam_count">1</td>')
        self.assertContains(self.response, '<td class="other_count">2</td>')


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

    def testAddInvalid(self):
        dc_form = forms.DocumentCategoryForm({'name': u'MöKomÄP', 'description': u'MoKomAP with invalid name'})
        self.assertFalse(dc_form.is_valid())
        dc_form = forms.DocumentCategoryForm({'name': u'MoKomAP', 'description': u'MoKomAP with valid name'})
        self.assertTrue(dc_form.is_valid())

    def testAddDuplicate(self):
        """Test whether DocumentCategory name field is unique"""
        models.DocumentCategory.objects.create(name='test', description='Test category')
        dc_form = forms.DocumentCategoryForm({'name': 'test', 'description': 'Another test category'})
        self.assertFalse(dc_form.is_valid())

    def testAddInsensitiveDuplicate(self):
        """Test whether DocumentCategory name field is unique in any case"""
        models.DocumentCategory.objects.create(name='test', description='Test category')
        dc_form = forms.DocumentCategoryForm({'name': 'Test', 'description': 'Another test category'})
        self.assertFalse(dc_form.is_valid())


class DocumentListViewTest(TestCase):
    fixtures = ['testdocs', 'testusers']
    taburl = '/dokumente/an1i/'

    def setUp(self):
        self.response = self.client.get(self.taburl)

    def testTitle(self):
        self.assertContains(self.response, '<h1>Dokumente An1I</h1>')

    def testDocumentTitle(self):
        soup = BeautifulSoup(self.response.content)
        h4 = soup.find('span', text='Analysis 1 Theoriesammlung').findParent('h4').prettify()
        self.assertIn('<span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">', h4)
        self.assertIn('<span class="label label-success">\n Zusammenfassung\n</span>', h4)
        self.assertIn('<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/deed.de" ' +
                      'title="Veröffentlicht unter der CC BY-NC-SA 3.0 Lizenz">', h4)
        self.assertIn('<span class="label">\n  CC BY-NC-SA 3.0\n </span>', h4)

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
        # Downloadcount shouldn't increase, as request was done from the same IP
        self.assertContains(response2, '<p>1 Download</p>')
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
        self.user = User.objects.get(pk=1)
        self.event = models.Event.objects.create(
            id=1,
            summary='Testbar',
            description=u'This is a bar where people drink and party to \
                          test the studentenportal event feature.',
            author=self.user,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59),
            location=u'Gebäude 13',
            url=u'http://hsr.ch/')

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
        self.assertContains(response, '<strong>Ort:</strong>')
        self.assertContains(response, 'Gebäude 13')
        self.assertContains(response, '<strong>Website:</strong>')
        self.assertContains(response, 'http://hsr.ch/')


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
        self.assertContains(response, '<select id="id_lecturer" name="lecturer">')
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

    def testAutoUpvote(self):
        """Test whether the added quote was automatically upvoted."""
        self.client.post('/zitate/add/', {
            'pk': 9000,
            'lecturer': '1',
            'quote': 'ich bin der töllscht!',
        })
        quote = models.Quote.objects.get(lecturer=1, quote='ich bin der töllscht!')
        assert quote.vote_sum() == 1, "Quote wasn't automatically upvoted..."


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
        self.assertContains(response, 'Diese Registrierung ist Studenten mit einer HSR-Email-Adresse vorbehalten')
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


class UserProfileViewTest(TestCase):
    fixtures = ['testusers']

    def setUp(self):
        self.client.login(username='testuser', password='test')

    def testFormSubmission(self):
        """Test whether a profile form submission gets saved correctly."""
        response = self.client.post('/profil/', {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'twitter': 'jdoe',
            'flattr': 'johndoe',
        })
        self.assertRedirects(response, '/profil/')
        user = User.objects.get(username='testuser')
        self.assertEqual('test@example.com', user.email)
        self.assertEqual('John', user.first_name)
        self.assertEqual('Doe', user.last_name)
        self.assertEqual('jdoe', user.twitter)
        self.assertEqual('johndoe', user.flattr)


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
