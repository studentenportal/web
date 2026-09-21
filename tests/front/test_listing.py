import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.front.listing import ListingMixin
from apps.tipps.models import Tipp

User = get_user_model()
rf = RequestFactory()


class StubList(ListingMixin):
    search_fields = ("summary", "description")
    sort_options = {
        "date": {"label": "Neueste", "order_by": ["-date"]},
        "summary": {"label": "Titel", "order_by": ["summary"]},
    }
    filter_options = {"author": "author"}


def make_stub_view(query_string):
    view = StubList()
    view.request = rf.get("/?%s" % query_string.lstrip("?"))
    view.filter_choices = {"author": [(u.pk, u.username) for u in User.objects.all()]}
    return view


@pytest.mark.django_db
def test_search_matches_summary_and_description(user):
    Tipp.objects.create(author=user, summary="Python Tricks", description="d")
    Tipp.objects.create(author=user, summary="Other", description="use virtualenv")

    view = make_stub_view("q=python")
    assert list(view.apply_listing(Tipp.objects.all()))[0].summary == "Python Tricks"

    view = make_stub_view("q=VIRTUALENV")
    assert (
        list(view.apply_listing(Tipp.objects.all()))[0].description == "use virtualenv"
    )


@pytest.mark.django_db
def test_search_empty_returns_all(user):
    Tipp.objects.create(author=user, summary="A", description="d")
    Tipp.objects.create(author=user, summary="B", description="d")

    view = make_stub_view("q=   ")
    assert view.apply_listing(Tipp.objects.all()).count() == 2


@pytest.mark.django_db
def test_search_no_results(user):
    Tipp.objects.create(author=user, summary="A", description="d")

    view = make_stub_view("q=doesnotexist")
    assert view.apply_listing(Tipp.objects.all()).count() == 0


@pytest.mark.django_db
def test_invalid_sort_falls_back_to_default(user):
    Tipp.objects.create(author=user, summary="A", description="d")

    view = make_stub_view("sort=nonsense")
    assert view.get_current_sort() == "date"

    view = make_stub_view("")
    assert view.get_current_sort() == "date"


@pytest.mark.django_db
def test_sort_applied(user):
    a = Tipp.objects.create(author=user, summary="Bravo", description="d")
    b = Tipp.objects.create(author=user, summary="Alpha", description="d")

    view = make_stub_view("sort=summary")
    ordered = list(view.apply_listing(Tipp.objects.all()))
    assert [t.pk for t in ordered] == [b.pk, a.pk]


@pytest.fixture
def tipps_by_two_users(user):
    other = User.objects.create_user(
        username="other", password="test", email="other@t.ch"
    )
    tipp_mine = Tipp.objects.create(author=user, summary="Mine", description="d")
    tipp_theirs = Tipp.objects.create(author=other, summary="Theirs", description="d")
    return tipp_mine, tipp_theirs


@pytest.mark.django_db
def test_filter_applied(user, tipps_by_two_users):
    tipp_mine, _ = tipps_by_two_users
    view = make_stub_view("author=%s" % user.pk)
    result = list(view.apply_listing(Tipp.objects.all()))
    assert [t.pk for t in result] == [tipp_mine.pk]


@pytest.mark.django_db
def test_unknown_filter_value_ignored(user, tipps_by_two_users):
    view = make_stub_view("author=99999")
    assert view.apply_listing(Tipp.objects.all()).count() == 2


@pytest.mark.django_db
def test_listing_context(user):
    view = make_stub_view("q=foo&sort=summary")
    context = view.listing_context()
    assert context["search_query"] == "foo"
    assert context["current_sort"] == "summary"
    assert [o["value"] for o in context["sort_options"]] == ["date", "summary"]
    assert [o["active"] for o in context["sort_options"]] == [False, True]
    assert context["sort_options"][1]["label"] == "Titel"
    assert context["filter_options"][0]["param"] == "author"
    assert context["list_action"] == "/"


@pytest.mark.django_db
def test_listing_context_default_sort(user):
    view = make_stub_view("")
    context = view.listing_context()
    assert context["current_sort"] == "date"
    assert context["search_query"] == ""
