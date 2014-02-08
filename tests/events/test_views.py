# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from model_mommy import mommy

from apps.events import models

User = get_user_model()


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
