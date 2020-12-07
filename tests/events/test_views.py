# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from apps.events import models

User = get_user_model()


### Pytest Fixtures ###


@pytest.fixture
def test_events(transactional_db):
    user1 = baker.make(
        get_user_model(), username="user1", first_name="User", last_name="1"
    )
    user2 = baker.make(get_user_model(), username="user2")

    dt1 = datetime.datetime(2012, 12, 21, 20, 0)
    dt2 = datetime.datetime(2012, 12, 22, 10, 0)

    baker.make(
        models.Event,
        summary="Weltuntergang",
        start_date=dt1.date(),
        start_time=dt1.time(),
        end_date=dt2.date(),
        end_time=dt2.time(),
        location="Gebäude 1",
        author=user1,
    )
    baker.make(
        models.Event,
        summary="Afterparty",
        start_date=dt2.date(),
        start_time=dt2.time(),
        end_date=dt2.date(),
        author=user2,
    )


### Tests ###


class EventsViewTest(TestCase):
    taburl = "/events/"

    def setUp(self):
        self.response = self.client.get(self.taburl)

    def testTitle(self):
        self.assertContains(self.response, "<h1>Events</h1>")

    def testContent(self):
        self.assertContains(self.response, "<h2>Kommende Veranstaltungen</h2>")
        self.assertContains(self.response, "<h2>Vergangene Veranstaltungen</h2>")

    def testNullAuthor(self):
        models.Event.objects.create(
            summary="Testbar",
            description="This is a bar where people drink and party to \
                          test the studentenportal event feature.",
            author=None,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59),
        )
        response = self.client.get(self.taburl)
        assert response.status_code == 200


class EventDetailViewTest(TestCase):
    def setUp(self):
        self.user = baker.make_recipe("apps.front.user")
        self.event = models.Event.objects.create(
            id=1,
            summary="Testbar",
            description="This is a bar where people drink and party to \
                          test the studentenportal event feature.",
            author=self.user,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59),
            location="Gebäude 13",
            url="http://hsr.ch/",
        )

    def tearDown(self):
        self.event.delete()

    def testTitle(self):
        response = self.client.get("/events/1/")
        self.assertContains(response, "<h1>Testbar</h1>")

    def testContent(self):
        response = self.client.get("/events/1/")
        self.assertContains(
            response,
            "<p>This is a bar where people drink and party \
                        to test the studentenportal event feature.</p>",
            html=True,
        )
        self.assertContains(response, "<strong>Start:</strong>")
        self.assertContains(response, "1. September 2010 19:30")
        self.assertContains(response, "<strong>Ende:</strong>")
        self.assertContains(response, "1. September 2010 23:59")
        self.assertContains(response, "<strong>Ort:</strong>")
        self.assertContains(response, "Gebäude 13")
        self.assertContains(response, "<strong>Website:</strong>")
        self.assertContains(response, "http://hsr.ch/")


@pytest.mark.django_db(transaction=True)
def test_ical_event1(client, test_events):
    response = client.get(reverse("events:event_calendar"))
    event = response.content.decode("utf-8").split("BEGIN:VEVENT")[1]
    assert "SUMMARY:Weltuntergang" in event
    assert "DTSTART:20121221T200000" in event
    assert "DTEND:20121222T100000" in event
    assert "COMMENT:Erfasst von User 1" in event


@pytest.mark.django_db(transaction=True)
def test_ical_event2(client, test_events):
    response = client.get(reverse("events:event_calendar"))
    event = response.content.decode("utf-8").split("BEGIN:VEVENT")[2]
    assert "SUMMARY:Afterparty" in event
    assert "DTSTART:20121222T100000" in event
    assert "DTEND:20121222T235959" in event
    assert "COMMENT:Erfasst von user2" in event
