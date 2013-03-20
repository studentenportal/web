# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.test import TestCase, SimpleTestCase, TransactionTestCase
from django.contrib.auth import models as auth_models

from apps.front import models
from . import serializers


class UserSerializerTest(TestCase):
    fixtures = ['testusers']

    def testRatings(self):
        user = auth_models.User.objects.get(pk=0)
        assert True
