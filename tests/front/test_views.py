# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from model_mommy import mommy


User = get_user_model()


def login(self):
    self.client.login(username='testuser', password='test')


class HomeViewTest(TestCase):
    def testHTTP200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(TestCase):
    def testUnauthRedirect(self):
        """An unauthenticated user should not get access to the profile detail page."""
        response = self.client.get('/profil/')
        self.assertEqual(response.status_code, 302)


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
        self.doc1 = mommy.make_recipe('apps.documents.document_summary', name='Document 1',
                         description='The first document.', uploader=self.user1)
        self.doc2 = mommy.make_recipe('apps.documents.document_summary', name='Document 2',
                         description='The second document.', uploader=self.user2)
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

    def testOwnDocuments(self):
        url = reverse('user', args=(self.user1.pk, self.user1.username))
        category = self.doc1.category.name
        response = self.client.get(url)
        # Own document should be listed
        self.assertContains(response, 'property="dct:title">{}</h3>'.format(self.doc1.name))
        # Foreign document should not be listed
        self.assertNotContains(response, 'property="dct:title">{}</h3>'.format(self.doc2.name))
        # Category should be displayed
        self.assertContains(response, "{0}</span>".format(category));

    def testOtherDocuments(self):
        url = reverse('user', args=(self.user2.pk, self.user2.username))
        category = self.doc2.category.name
        response = self.client.get(url)
        # Own document should be listed
        self.assertContains(response, 'property="dct:title">{}</h3>'.format(self.doc2.name))
        # Foreign document should not be listed
        self.assertNotContains(response, 'property="dct:title">{}</h3>'.format(self.doc1.name))
        # Category should be displayed
        self.assertContains(response, "{0}</span>".format(category));


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
