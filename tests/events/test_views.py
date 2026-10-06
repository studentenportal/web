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
        repeats=False,
    )

    baker.make(
        models.Event,
        summary="Afterparty",
        start_date=dt2.date(),
        start_time=dt2.time(),
        end_date=dt2.date(),
        author=user2,
        repeats=False,
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
            url="https://ost.ch/",
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
        self.assertContains(response, "https://ost.ch/")


@pytest.mark.django_db(transaction=True)
def test_recurring_event_list(client, transactional_db):
    """Recurring events should appear multiple times in the event list."""
    user = baker.make(get_user_model(), username="recur_user")
    # Create a recurring event in the future
    import datetime as dt

    future_date = dt.date.today() + dt.timedelta(days=7)
    models.Event.objects.create(
        summary="Weekly Meeting",
        description="Recurring test",
        author=user,
        start_date=future_date,
        repeats=True,
        repeat_every=1,
        repeat_unit="week",
        repeat_ends=future_date + dt.timedelta(days=21),
    )
    response = client.get("/events/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert content.count("Weekly Meeting") == 4  # original + 3 copies


@pytest.mark.django_db(transaction=True)
def test_recurring_event_shows_label(client, transactional_db):
    """Recurring event copies should show the recurring indicator."""
    user = baker.make(get_user_model(), username="label_user")
    import datetime as dt

    future_date = dt.date.today() + dt.timedelta(days=7)
    models.Event.objects.create(
        summary="Repeater",
        description="Test",
        author=user,
        start_date=future_date,
        repeats=True,
        repeat_every=1,
        repeat_unit="week",
        repeat_ends=future_date + dt.timedelta(days=14),
    )
    response = client.get("/events/")
    content = response.content.decode("utf-8")
    # The 2 copies (not the original) should have the recurring label
    assert content.count("Wiederkehrend") == 2


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


### Standardized listing tests (pytest style) ###


@pytest.mark.django_db
def test_event_list_search(client):
    today = datetime.date.today()
    models.Event.objects.create(
        summary="Foo Bar",
        description="d",
        start_date=today + datetime.timedelta(days=1),
    )
    models.Event.objects.create(
        summary="Baz Event",
        description="d",
        start_date=today + datetime.timedelta(days=2),
    )
    content = client.get("/events/", {"q": "baz"}).content.decode()
    assert "Baz Event" in content
    assert "Foo Bar" not in content


@pytest.mark.django_db
def test_event_list_search_past_events(client):
    today = datetime.date.today()
    models.Event.objects.create(
        summary="Old Bar",
        description="d",
        start_date=today - datetime.timedelta(days=3),
    )
    models.Event.objects.create(
        summary="Old Baz",
        description="d",
        start_date=today - datetime.timedelta(days=4),
    )
    content = client.get("/events/", {"q": "old"}).content.decode()
    assert "Old Bar" in content
    assert "Old Baz" in content
    content = client.get("/events/", {"q": "bar"}).content.decode()
    assert "Old Bar" in content
    assert "Old Baz" not in content


@pytest.mark.django_db
def test_rss_feed_contains_upcoming_events(client):
    today = datetime.date.today()
    models.Event.objects.create(
        summary="Future Bar",
        description="A bar in the future",
        start_date=today + datetime.timedelta(days=1),
        start_time=datetime.time(19, 0),
        location="Gebäude 1",
    )
    models.Event.objects.create(
        summary="Past Bar",
        description="A bar in the past",
        start_date=today - datetime.timedelta(days=1),
    )
    response = client.get(reverse("events:event_feed"))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/rss+xml")
    content = response.content.decode("utf-8")
    assert "Future Bar" in content
    assert "A bar in the future" in content
    assert "Ort: Gebäude 1" in content
    assert "/events/" in content
    assert "Past Bar" not in content


@pytest.mark.django_db
def test_event_list_past_pagination(client):
    today = datetime.date.today()
    for i in range(55):
        models.Event.objects.create(
            summary="Past %02d" % i,
            description="d",
            start_date=today - datetime.timedelta(days=i + 1),
        )
    content = client.get("/events/").content.decode()
    assert 'class="pagination"' in content
    assert "?page=2" in content
    # The oldest events only appear on the second page
    content = client.get("/events/", {"page": 2}).content.decode()
    assert "Past 54" in content
    content = client.get("/events/").content.decode()
    assert "Past 54" not in content
