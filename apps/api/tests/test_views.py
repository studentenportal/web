# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth import get_user_model

from model_mommy import mommy
from provider.constants import CONFIDENTIAL
from provider.oauth2 import models as oauth2_models

from apps.front import models


User = get_user_model()


### HELPERS ###

def login(self):
    self.client.login(username='testuser', password='test')


### BASE CLASSES ###

class BaseTest(TestCase):
    def setUp(self):
        self.user = mommy.make_recipe('apps.front.user')
        self.client = Client(ACCEPT='application/json')


class AuthenticatedTest(BaseTest):
    def setUp(self):
        super(AuthenticatedTest, self).setUp()
        login(self)


### TESTS ###

class AuthenticationTest(BaseTest):

    def testNoauth(self):
        """Test that requesting resources is not possible without auth."""
        targets = ['api_root', 'user_list', 'user_detail', 'lecturer_list',
                   'lecturer_detail', 'quote_list', 'quote_detail']
        for target in targets:
            try:
                url = reverse('api:' + target)
            except NoReverseMatch:
                url = reverse('api:' + target, args=(1,))
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 403,
                    'Status code for %s is %d instead of 403.' % (url, resp.status_code))
            data = json.loads(resp.content)
            self.assertEqual(data, {
                'detail': 'Authentication credentials were not provided.'
            })

    def testSessionAuth(self):
        url = reverse('api:quote_list')
        login(self)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def testOAuth2(self):
        # Create an OAuth2 Client object
        oauth2_client = mommy.make(oauth2_models.Client,
            user=self.user,
            url='http://example.com/',
            redirect_uri='http://example.com/',
            client_type=CONFIDENTIAL,
        )
        # Obtain access token via POST
        resp = self.client.post(reverse('oauth2:access_token'), {
            'client_id': oauth2_client.client_id,
            'client_secret': oauth2_client.client_secret,
            'grant_type': 'password',
            'username': 'testuser',
            'password': 'test',
        })
        data = json.loads(resp.content)
        # Try to access API
        url = reverse('api:quote_list')
        resp1 = self.client.get(url)
        self.assertEqual(resp1.status_code, 403)
        resp2 = self.client.get(url, HTTP_AUTHORIZATION='Bearer {}'.format(data['access_token']))
        self.assertEqual(resp2.status_code, 200)


class UserViewTest(AuthenticatedTest):

    def testStatusCode(self):
        urls = [reverse('api:user_list'), reverse('api:user_detail', args=(self.user.pk,))]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200,
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code))

    def testListData(self):
        users = [mommy.make(User) for i in xrange(3)]
        url = reverse('api:user_list')
        resp = self.client.get(url)
        data = json.loads(resp.content)
        self.assertEqual(len(data['results']), data['count'])
        self.assertEqual(data['count'], User.objects.count())

    def testDetailData(self):
        url = reverse('api:user_detail', args=(self.user.pk,))
        resp = self.client.get(url)
        data = json.loads(resp.content)
        self.assertTrue(data['url'].startswith('http://'))
        attrs = ['username', 'first_name', 'last_name', 'email', 'flattr', 'twitter']
        for attr in attrs:
            self.assertEqual(data[attr], getattr(self.user, attr))

    def testListMethods(self):
        url = reverse('api:user_list')
        resp = self.client.head(url)
        self.assertEqual(resp.get('Allow'), 'GET, HEAD, OPTIONS')

    def testDetailMethods(self):
        url = reverse('api:user_detail', args=(self.user.pk,))
        resp = self.client.head(url)
        self.assertEqual(resp.get('Allow'), 'GET, PUT, HEAD, OPTIONS, PATCH')

    def testUpdatePermissions(self):
        """It should only be possible to edit own user."""
        another_user = mommy.make(User)
        url1 = reverse('api:user_detail', args=(self.user.pk,))
        url2 = reverse('api:user_detail', args=(another_user.pk,))
        data1 = {'username': 'test1', 'email': 'test1@example.com'}
        data2 = {'username': 'test2', 'email': 'test2@example.com'}
        resp1 = self.client.put(url1, json.dumps(data1), 'application/json')
        resp2 = self.client.put(url2, json.dumps(data2), 'application/json')
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 403)

    def testUsernameChange(self):
        """You should not be able to change your own username."""
        url = reverse('api:user_detail', args=(self.user.pk,))
        data = {'username': 'a_new_username', 'email': self.user.email}
        resp = self.client.put(url, json.dumps(data), 'application/json')
        self.assertEqual(resp.status_code, 200)
        newuser = User.objects.get(pk=self.user.pk)
        self.assertEqual(self.user.username, newuser.username)


class LecturerViewTest(AuthenticatedTest):

    def setUp(self):
        super(LecturerViewTest, self).setUp()
        self.lecturer = mommy.make(models.Lecturer)

    def testStatusCode(self):
        urls = [reverse('api:lecturer_list'), reverse('api:lecturer_detail', args=(self.lecturer.pk,))]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200,
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code))

    def testDetailData(self):
        [mommy.make(models.Quote, lecturer=self.lecturer) for i in xrange(3)]

        url = reverse('api:lecturer_detail', args=(self.lecturer.pk,))
        resp = self.client.get(url)
        data = json.loads(resp.content)

        self.assertTrue(data['url'].startswith('http://'))

        attrs = ['title', 'last_name', 'first_name', 'abbreviation',
                 'department', 'function', 'main_area', 'subjects', 'email',
                 'office']
        for attr in attrs:
            self.assertEqual(data[attr], getattr(self.lecturer, attr))

        self.assertEqual(len(data['quotes']), self.lecturer.Quote.count())
        for quote in data['quotes']:
            self.assertTrue(quote.startswith('http://'))

    def testListMethods(self):
        url = reverse('api:lecturer_list')
        resp = self.client.head(url)
        self.assertEqual(resp.get('Allow'), 'GET, HEAD, OPTIONS')

    def testDetailMethods(self):
        url = reverse('api:lecturer_detail', args=(self.lecturer.pk,))
        resp = self.client.head(url)
        self.assertEqual(resp.get('Allow'), 'GET, HEAD, OPTIONS')


class QuoteViewTest(AuthenticatedTest):

    def setUp(self):
        super(QuoteViewTest, self).setUp()
        self.quote = mommy.make(models.Quote, author=self.user)

    def testStatusCode(self):
        urls = [reverse('api:quote_list'), reverse('api:quote_detail', args=(self.quote.pk,))]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200,
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code))

    def testDetailData(self):
        url = reverse('api:quote_detail', args=(self.quote.pk,))
        resp = self.client.get(url)
        data = json.loads(resp.content)
        self.assertTrue(data['url'].startswith('http://'))
        self.assertTrue(data['lecturer'].startswith('http://'))
        self.assertEqual(data['lecturer_name'], self.quote.lecturer.name())
        self.assertEqual(data['date'][:10], self.quote.date.date().isoformat())
        self.assertEqual(data['comment'], self.quote.comment)

    def testListMethods(self):
        url = reverse('api:quote_list')
        resp = self.client.head(url)
        self.assertEqual(resp.get('Allow'), 'GET, POST, HEAD, OPTIONS')

    def testDetailMethods(self):
        url = reverse('api:quote_detail', args=(self.quote.pk,))
        resp = self.client.head(url)
        self.assertEqual(resp.get('Allow'), 'GET, PUT, HEAD, OPTIONS, PATCH')

    def testAutoAuthorPOST(self):
        """Assert that the author is automatically set to the currently logged
        in user on POST."""
        # Insert two quotes
        url = reverse('api:quote_list')
        lecturer = mommy.make(models.Lecturer)
        other_user = mommy.make(User)
        resp = self.client.post(url, {
            'lecturer': reverse('api:lecturer_detail', args=(lecturer.pk,)),
            'quote': 'This is a test.',
            'comment': 'No author'
        })
        self.assertEqual(resp.status_code, 201)
        resp = self.client.post(url, {
            'lecturer': reverse('api:lecturer_detail', args=(lecturer.pk,)),
            'author': reverse('api:user_detail', args=(other_user.pk,)),
            'quote': 'This is a test.',
            'comment': 'With author'
        })
        self.assertEqual(resp.status_code, 201)
        # Assert that two quotes were created.
        quote1 = models.Quote.objects.filter(comment='No author')
        quote2 = models.Quote.objects.filter(comment='With author')
        self.assertTrue(quote1.exists())
        self.assertTrue(quote2.exists())
        # Assert that the author is the currently logged in user
        self.assertEqual(quote1.get().author, self.user)
        self.assertEqual(quote2.get().author, self.user)

    def testAutoAuthorPUT(self):
        """Assert that the author is automatically set to the currently logged
        in user on PUT."""
        # Update existing quote with new comment and author
        url = reverse('api:quote_detail', args=(self.quote.pk,))
        other_user = mommy.make(User)
        data = {
            'lecturer': reverse('api:lecturer_detail', args=(self.quote.lecturer.pk,)),
            'quote': self.quote.quote,
            'comment': 'newcomment',
            'author': reverse('api:user_detail', args=(other_user.pk,)),
        }
        resp = self.client.put(url, json.dumps(data), 'application/json')
        # Assert that the PUT request was processed
        self.assertEqual(resp.status_code, 200)
        # Comment should be changed, but not the author
        newquote = models.Quote.objects.get(pk=self.quote.pk)
        self.assertEqual(newquote.comment, 'newcomment')
        self.assertEqual(newquote.author, self.user)

    def testUpdatePermissions(self):
        """It should only be possible to edit own quotes."""
        quote1 = self.quote
        quote2 = mommy.make(models.Quote)
        url1 = reverse('api:quote_detail', args=(quote1.pk,))
        url2 = reverse('api:quote_detail', args=(quote2.pk,))
        data = {
            'lecturer': reverse('api:lecturer_detail', args=(quote1.lecturer.pk,)),
            'quote': 'testquote',
            'comment': 'testcomment',
        }
        resp1 = self.client.put(url1, json.dumps(data), 'application/json')
        resp2 = self.client.put(url2, json.dumps(data), 'application/json')
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 403)

    def testAuthorChange(self):
        """You should not be able to change the author of a quote."""
        url = reverse('api:quote_detail', args=(self.quote.pk,))
        another_user = mommy.make(User)
        data = {
            'lecturer': reverse('api:lecturer_detail', args=(self.quote.lecturer.pk,)),
            'quote': self.quote.quote,
            'comment': self.quote.comment,
            'author': reverse('api:user_detail', args=(another_user.pk,)),
        }
        resp = self.client.put(url, json.dumps(data), 'application/json')
        self.assertEqual(resp.status_code, 200)
        newquote = models.Quote.objects.get(pk=self.quote.pk)
        self.assertEqual(self.quote.author, newquote.author)
