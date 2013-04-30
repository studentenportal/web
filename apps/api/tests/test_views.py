# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth import get_user_model

from model_mommy import mommy

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


class UserViewTest(AuthenticatedTest):

    def testStatusCode(self):
        urls = [reverse('api:user_list'), reverse('api:user_detail', args=(self.user.pk,))]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200,
                    'Status code for %s is %d instead of 200.' % (url, resp.status_code))
