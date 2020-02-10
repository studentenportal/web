# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from django.test import TestCase
from django.core import mail
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import transaction

from pytest_django.asserts import assertRedirects


from model_bakery import baker


User = get_user_model()


def login(self):
    assert self.client.login(username='testuser', password='test')


@pytest.mark.django_db
def test_home_view(client):
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_view_unauth_redirect(client):
    """An unauthenticated user should not get access to the profile detail page."""
    response = client.get('/profil/')
    assert response.status_code == 302


class LoginTest(TestCase):
    url = '/accounts/login/'

    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')

    def testTitle(self):
        r = self.client.get(self.url)
        self.assertContains(r, '<h1>Login</h1>')

    def testLogin(self):
        r1 = self.client.get('/zitate/')
        assert r1.status_code == 302
        login(self)
        r2 = self.client.get('/zitate/')
        assert r2.status_code == 200

    def testCaseInsensitveLogin(self):
        r1 = self.client.post(self.url, {'username': 'testuser', 'password': 'test'})
        assert r1.status_code == 302
        r2 = self.client.post(self.url, {'username': 'Testuser', 'password': 'test'})
        assert r2.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_registration(client):
    """
    Test that a registration is successful and that an activation email is
    sent.

    Needs to use a transaction because the mail is sent on on_commit.
    """
    registration_url = '/accounts/register/'

    response = client.post(registration_url, {
        'email': 'testuser@hsr.ch',
        'password1': 'testpass',
        'password2': 'testpass',
    })
    assertRedirects(response, '/accounts/register/complete/')
    assert User.objects.filter(username='testuser').exists()

    transaction.commit()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == '[studentenportal.ch] Aktivierung'


class RegistrationViewTest(TestCase):
    registration_url = '/accounts/register/'

    def testRegistrationPage(self):
        response = self.client.get(self.registration_url)
        self.assertContains(response, '<h1>Registrieren</h1>')
        self.assertContains(response, 'Diese Registrierung ist Studenten mit einer HSR-Email-Adresse')
        self.assertContains(response, '<form')

    def testRegistrationBadUsername(self):
        """
        Test that a registration with a bad username returns an error.
        """
        response = self.client.post(self.registration_url, {
            'email': 'a+++@hsr.ch',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        assert response.status_code == 200
        assert u'Ungültige E-Mail' in response.content.decode('utf8')

    def testRegistrationBadDomain(self):
        """
        Test that a registration with a non-hsr.ch Domain return an error.
        """
        response = self.client.post(self.registration_url, {
            'email': 'ameier@zhaw.ch',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        assert response.status_code == 200
        assert u'Registrierung ist Studenten mit einer @hsr.ch-Mailadresse vorbehalten' \
                in response.content.decode('utf8')

    def testRegistrationDoubleUsername(self):
        """
        Test that a registration with a bad username returns an error.
        """
        baker.make(User, username='a', email='abc@hsr.ch')
        response = self.client.post(self.registration_url, {
            'email': 'a@hsr.ch',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        assert response.status_code == 200
        assert u'Benutzer &quot;a&quot; existiert bereits' in response.content.decode('utf8')

    def testRegistrationDoubleEmail(self):
        """
        Test that a registration with a bad username returns an error.
        """
        baker.make(User, username='abc', email='a@hsr.ch')
        response = self.client.post(self.registration_url, {
            'email': 'a@hsr.ch',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        assert response.status_code == 200
        assert u'Benutzer mit dieser E-Mail existiert bereits.' in response.content.decode('utf8')


class UserViewTest(TestCase):

    def setUp(self):
        # setUpClass
        self.user1 = baker.make_recipe('apps.front.user')
        self.user2 = baker.make(User, first_name='Another', last_name='Guy',
                                      email='test2@studentenportal.ch')
        self.doc1 = baker.make_recipe('apps.documents.document_summary', name='Document 1',
                         description='The first document.', uploader=self.user1, document='a.pdf')
        self.doc2 = baker.make_recipe('apps.documents.document_summary', name='Document 2',
                         description='The second document.', uploader=self.user2, document='b.pdf')
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
        baker.make_recipe('apps.front.user')
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
        assert user.email == 'test@studentenportal.ch'  # No change!
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.twitter == 'jdoe'
        assert user.flattr == 'johndoe'


class StatsViewTest(TestCase):
    taburl = '/statistiken/'

    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')

    def testLoginRequired(self):
        response = self.client.get(self.taburl)
        self.assertRedirects(response, '/accounts/login/?next=/statistiken/')

    def testTitle(self):
        login(self)
        response = self.client.get(self.taburl)
        self.assertContains(response, '<h1>Statistiken</h1>')
