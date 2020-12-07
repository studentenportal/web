# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from model_bakery import baker

from apps.events import models

User = get_user_model()


@pytest.mark.django_db
class TestEventModel:
    def test_date_time_event(self):
        user = baker.make(User, username="testuser")
        event = models.Event.objects.create(
            summary="Testbar",
            description="This is a bar where people drink and party to \
                          test the studentenportal event feature.",
            author=user,
            start_date=datetime.date(day=1, month=9, year=2010),
            start_time=datetime.time(hour=19, minute=30),
            end_time=datetime.time(hour=23, minute=59),
        )

        assert event.summary == "Testbar"
        assert event.end_date is None
        assert event.author.username == "testuser"
        assert event.is_over()
        assert event.days_until() is None

    def test_all_day_event(self):
        user = baker.make(User)
        start_date = datetime.date.today() + datetime.timedelta(days=365)
        event = models.Event.objects.create(
            summary="In a year",
            description="This happens in a year from now.",
            author=user,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=1),
        )

        assert event.summary == "In a year"
        assert event.start_time is None
        assert event.end_time is None
        assert not event.is_over()
        assert event.all_day()
        assert event.days_until() == 365

    def test_null_value_author(self):
        event = models.Event()
        event.summary = "Testbar"
        event.description = "Dies ist eine bar deren autor nicht mehr existiert."
        event.author = None
        event.start_date = datetime.date(day=1, month=9, year=2010)
        event.start_time = datetime.time(hour=19, minute=30)
        event.end_time = datetime.time(hour=23, minute=59)
        try:
            event.save()
        except IntegrityError:
            pytest.fail("An event with no author should not throw an IntegrityError.")
