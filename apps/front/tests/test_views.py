# -*- coding: utf-8 -*-
import datetime
import os

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from BeautifulSoup import BeautifulSoup
from model_mommy import mommy

from apps.front import models, forms


User = get_user_model()


def login(self):
    self.client.login(username='testuser', password='test')


class HomeViewTest(TestCase):
    def testHTTP200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class LecturerListViewTest(TestCase):
    def testLoginRequired(self):
        response = self.client.get('/dozenten/')
        self.assertRedirects(response, '/accounts/login/?next=/dozenten/')

    def testContent(self):
        mommy.make_recipe('apps.front.user')
        mommy.make_recipe('apps.front.lecturer')
        login(self)
        response = self.client.get('/dozenten/')
        self.assertContains(response, '<h1>Unsere Dozenten</h1>')
        self.assertContains(response, 'Prof. Dr. Krakaduku David')


class LecturerDetailViewTest(TestCase):
    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')
        self.lecturer = mommy.make_recipe('apps.front.lecturer')
        self.url = reverse('lecturer_detail', args=(self.lecturer.pk,))

    def testLoginRequired(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.url)

    def testDescription(self):
        login(self)
        response = self.client.get(self.url)
        self.assertContains(response, '<h1 class="lecturer-name" ' + \
                'data-lecturer-pk="%s">Prof. Dr. Krakaduku David</h1>' % self.lecturer.pk)
        self.assertContains(response, 'Quantenphysik, Mathematik für Mathematiker')

    def testContact(self):
        login(self)
        response = self.client.get(self.url)
        self.assertContains(response, '1.337')
        self.assertContains(response, 'krakaduku@hsr.ch')


class ProfileViewTest(TestCase):
    def testUnauthRedirect(self):
        """An unauthenticated user should not get access to the profile detail page."""
        response = self.client.get('/profil/')
        self.assertEqual(response.status_code, 302)


class DocumentDownloadTest(TestCase):
    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')

    def testSummaryServed(self):
        """Assert that the summaries get served, even without login."""
        doc = mommy.make_recipe('apps.front.document_summary')
        url = reverse('document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testExamRequireLogin(self):
        """Assert that the exams require login."""
        doc = mommy.make_recipe('apps.front.document_exam')
        url = reverse('document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        category_path = reverse('document_list', args=(doc.category.name.lower(),))
        self.assertRedirects(response, '/accounts/login/?next=%s' % category_path)

    def testExamServed(self):
        """Assert that the exams get served when logged in."""
        login(self)
        doc = mommy.make_recipe('apps.front.document_exam')
        url = reverse('document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testUmlautDocumentServed(self):
        """Test whether documents with umlauts in their original filename can
        be served."""
        doc = mommy.make_recipe('apps.front.document_summary', original_filename='Füübäär Søreņ')
        url = reverse('document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class DocumentcategoryListViewTest(TestCase):
    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')
        mommy.make_recipe('apps.front.document_summary')
        mommy.make_recipe('apps.front.document_summary')
        mommy.make_recipe('apps.front.document_exam')
        mommy.make_recipe('apps.front.document_software')
        mommy.make_recipe('apps.front.document_learning_aid')
        # setUp
        self.response = self.client.get(reverse('documentcategory_list'))

    def testTitle(self):
        self.assertContains(self.response, '<h1>Dokumente</h1>')

    def testModuleName(self):
        """Test whether the module An1I appears in the list."""
        self.assertContains(self.response, '<strong>An1I</strong>')
        self.assertContains(self.response, 'Analysis 1 für Informatiker')

    def testUserAddButton(self):
        """Test whether the add button is shown when and only when the user is logged in."""
        self.assertNotContains(self.response, 'Modul hinzufügen')
        login(self)
        logged_in_response = self.client.get(reverse('documentcategory_list'))
        self.assertContains(logged_in_response, 'Modul hinzufügen')

    def testCounts(self):
        """Test whether the category counts are correct."""
        self.assertContains(self.response, '<td class="summary_count">2</td>')
        self.assertContains(self.response, '<td class="exam_count">1</td>')
        self.assertContains(self.response, '<td class="other_count">2</td>')


class DocumentcategoryAddViewTest(TestCase):
    taburl = '/dokumente/add/'

    def setUp(self):
        mommy.make_recipe('apps.front.user')
        login(self)

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
    def setUp(self):
        # setUpClass
        self.user1 = mommy.make_recipe('apps.front.user')
        self.user2 = mommy.make(User, first_name='Another', last_name='Guy')
        self.doc1 = mommy.make_recipe('apps.front.document_summary',
                         name='Analysis 1 Theoriesammlung',
                         description='Theorie aus dem AnI1-Skript auf 8 Seiten',
                         uploader=self.user1,
                         upload_date='2011-12-18 01:28:52',
                         change_date='2011-12-18 01:28:52',
                         license=5)
        self.doc2 = mommy.make_recipe('apps.front.document_summary', uploader=self.user2)
        self.doc3 = mommy.make_recipe('apps.front.document_exam', uploader=self.user1)
        self.doc4 = mommy.make_recipe('apps.front.document_software', uploader=self.user1)
        self.doc5 = mommy.make_recipe('apps.front.document_learning_aid', uploader=self.user1)
        self.category = self.doc1.category
        # setUp
        self.url = reverse('document_list', args=(self.category.name.lower(),))
        self.response = self.client.get(self.url)

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
        url = reverse('document_edit', args=(self.doc1.category.name.lower(), self.doc1.pk))
        self.assertNotContains(self.response, 'href="{}"'.format(url))

    def testEditButtonLoggedIn(self):
        login(self)
        url1 = reverse('document_edit', args=(self.doc1.category.name.lower(), self.doc1.pk))
        url2 = reverse('document_edit', args=(self.doc2.category.name.lower(), self.doc2.pk))
        response = self.client.get(self.url)
        self.assertContains(response, 'href="{}"'.format(url1))
        self.assertNotContains(response, 'href="{}"'.format(url2))

    def testDeleteButtonLoggedOut(self):
        url = reverse('document_delete', args=(self.doc1.category.name.lower(), self.doc1.pk))
        self.assertNotContains(self.response, 'href="{}"'.format(url))

    def testDeleteButtonLoggedIn(self):
        login(self)
        url1 = reverse('document_delete', args=(self.doc1.category.name.lower(), self.doc1.pk))
        url2 = reverse('document_delete', args=(self.doc2.category.name.lower(), self.doc2.pk))
        response = self.client.get(self.url)
        self.assertContains(response, 'href="{}"'.format(url1))
        self.assertNotContains(response, 'href="{}"'.format(url2))

    def testDownloadCount(self):
        doc = mommy.make_recipe('apps.front.document_summary')
        dl_url = reverse('document_download', args=(doc.category.name.lower(), doc.pk))

        # No downloads yet
        response0 = self.client.get(self.url)
        soup0 = BeautifulSoup(response0.content)
        anchor0 = soup0.find('a', href=dl_url)
        self.assertEqual(anchor0.parent()[-1].text, '0 Downloads')

        # First download
        self.client.get(dl_url)
        response1 = self.client.get(self.url)
        soup1 = BeautifulSoup(response1.content)
        anchor1 = soup1.find('a', href=dl_url)
        self.assertEqual(anchor1.parent()[-1].text, '1 Download')

        # Second download. Downloadcount shouldn't increase, as request was
        # done from the same IP
        self.client.get(dl_url)
        response2 = self.client.get(self.url)
        soup2 = BeautifulSoup(response2.content)
        anchor2 = soup2.find('a', href=dl_url)
        self.assertEqual(anchor2.parent()[-1].text, '1 Download')

    def testNullValueUploader(self):
        """Test whether a document without an uploader does not raise an error."""
        doc = mommy.make_recipe('apps.front.document_summary',
                name='Analysis 1 Theoriesammlung',
                description='Dieses Dokument ist eine Zusammenfassung der',
                uploader=None)
        url = reverse('document_list', args=(doc.category.name.lower(),))
        response = self.client.get(url)
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
    def setUp(self):
        self.user = mommy.make_recipe('apps.front.user')
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
    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')
        mommy.make_recipe('apps.front.lecturer')
        # setUp
        login(self)

    def testGenericForm(self):
        """Test the form that is shown if no lecturer is preselected."""
        response = self.client.get('/zitate/add/')
        self.assertContains(response, '<h1>Zitat hinzufügen</h1>')
        self.assertContains(response, '<option value="" selected="selected">---------</option>')

    def testPrefilledForm(self):
        """Test the form that is shown if a lecturer is preselected."""
        response = self.client.get('/zitate/1337/add/')
        self.assertContains(response, '<h1>Zitat hinzufügen</h1>')
        self.assertContains(response, '<select id="id_lecturer" name="lecturer">')
        self.assertContains(response, '<option value="1337" selected="selected">Krakaduku David</option>')

    def testFormSubmission(self):
        """Test whether a quote submission gets saved correctly."""
        response = self.client.post('/zitate/add/', {
            'lecturer': '1337',
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
            'lecturer': '1337',
            'quote': 'ich bin der töllscht!',
        })
        quote = models.Quote.objects.get(lecturer=1337, quote='ich bin der töllscht!')
        assert quote.vote_sum() == 1, "Quote wasn't automatically upvoted..."


class QuoteViewTest(TestCase):
    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')
        # setUp
        login(self)
        self.response = self.client.get('/zitate/')

    def testTitle(self):
        self.assertContains(self.response, '<h1>Zitate</h1>')

    def testQuoteInList(self):
        """Test whether an added quote shows up in the list."""
        mommy.make(models.Quote, quote='spam', comment='ham')
        response = self.client.get('/zitate/')
        self.assertContains(response, 'spam')
        self.assertContains(response, 'ham')

    def testNullValueAuthor(self):
        """Test whether a quote without an author does not raise an error."""
        mommy.make(models.Quote, quote='spam', comment='ham', author=None)
        response = self.client.get('/zitate/')
        self.assertContains(response, 'spam')
        self.assertContains(response, 'ham')


class LoginTest(TestCase):
    url = '/accounts/login/'

    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')

    def testTitle(self):
        r = self.client.get(self.url)
        self.assertContains(r, '<h1>Login</h1>')

    def testLogin(self):
        r1 = self.client.get('/zitate/')
        self.assertEqual(r1.status_code, 302)
        login(self)
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
    def setUp(self):
        # setUpClass
        self.user1 = mommy.make_recipe('apps.front.user')
        self.user2 = mommy.make(User, first_name='Another', last_name='Guy',
                                      email='test2@studentenportal.ch')
        # setUp
        login(self)

    def testOwnUserView(self):
        url = reverse('user', args=(self.user1.pk, self.user1.username))
        response = self.client.get(url)
        self.assertContains(response, '<h1>testuser</h1>')
        self.assertContains(response, 'test@studentenportal.ch')

    def testOtherUserView(self):
        url = reverse('user', args=(self.user2.pk, self.user2.username))
        response = self.client.get(url)
        self.assertContains(response, '<h1>Another Guy</h1>')
        self.assertContains(response, 'test2@studentenportal.ch')


class UserProfileViewTest(TestCase):
    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')
        # setUp
        login(self)

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
    taburl = '/statistiken/'

    def setUp(self):
        # setUpClass
        mommy.make_recipe('apps.front.user')

    def testLoginRequired(self):
        response = self.client.get(self.taburl)
        self.assertRedirects(response, '/accounts/login/?next=/statistiken/')

    def testTitle(self):
        login(self)
        response = self.client.get(self.taburl)
        self.assertContains(response, '<h1>Statistiken</h1>')
