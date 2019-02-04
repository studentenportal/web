# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from model_mommy import mommy

from apps.api import serializers


class UserSerializerTest(TestCase):

    def testSerialization(self):
        """A simple serialization test case."""
        user = mommy.make(get_user_model(), flattr='flttr', twitter='twttr')
        serializer = serializers.UserSerializer(user)
        data = serializer.data
        self.assertEqual(data, {
            'id': user.pk,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'flattr': 'flttr',
            'twitter': 'twttr',
            'quotes': [],
        })
