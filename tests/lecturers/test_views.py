import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from apps.lecturers import models

User = get_user_model()


def login(self):
    assert self.client.login(username="testuser", password="test")


class LecturerListViewTest(TestCase):
    def testLoginRequired(self):
        response = self.client.get("/dozenten/")
        self.assertRedirects(response, "/accounts/login/?next=/dozenten/")

    def testContent(self):
        baker.make_recipe("apps.front.user")
        baker.make_recipe("apps.lecturers.lecturer")
        login(self)
        response = self.client.get("/dozenten/")
        self.assertContains(response, "<h1>Unsere Dozenten</h1>")
        self.assertContains(response, "David<br />Krakaduku")

    def testSearch(self):
        """Search must filter over all lecturers, not only the current page."""
        baker.make_recipe("apps.front.user")
        baker.make_recipe("apps.lecturers.lecturer")
        baker.make(models.Lecturer, first_name="Albert", last_name="Einstein")
        login(self)

        response = self.client.get("/dozenten/", {"q": "krakaduku"})
        self.assertContains(response, "David<br />Krakaduku")
        self.assertNotContains(response, "Einstein")

        response = self.client.get("/dozenten/", {"q": "einstein"})
        self.assertContains(response, "Albert<br />Einstein")
        self.assertNotContains(response, "Krakaduku")

    def testSearchNoResults(self):
        baker.make_recipe("apps.front.user")
        baker.make_recipe("apps.lecturers.lecturer")
        login(self)
        response = self.client.get("/dozenten/", {"q": "doesnotexist"})
        self.assertContains(response, "Keine passenden Dozenten gefunden.")

    def testPagination(self):
        baker.make_recipe("apps.front.user")
        for i in range(55):
            baker.make(models.Lecturer, abbreviation="b%03d" % i)
        login(self)
        response = self.client.get("/dozenten/")
        self.assertContains(response, 'class="pagination"')
        self.assertContains(response, "?page=2")


class LecturerDetailViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe("apps.front.user")
        self.lecturer = baker.make_recipe("apps.lecturers.lecturer")
        self.url = reverse("lecturers:lecturer_detail", args=(self.lecturer.pk,))

    def testLoginRequired(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/accounts/login/?next=%s" % self.url)

    def testDescription(self):
        login(self)
        response = self.client.get(self.url)
        title = (
            '<h1 class="lecturer-name" '
            'data-lecturer-pk="%s" '
            'data-rating-url="/api/v1/lecturers/%s/rate"'
            ">Prof. Dr. Krakaduku David</h1>" % (self.lecturer.pk, self.lecturer.pk)
        )
        self.assertContains(response, title)
        self.assertContains(response, "Quantenphysik, Mathematik für Mathematiker")

    def testContact(self):
        login(self)
        response = self.client.get(self.url)
        self.assertContains(response, "1.337")
        self.assertContains(response, "kraka.duku@ost.ch")


@pytest.mark.django_db
def test_lecturer_add(auth_client):
    first_name = "Albert"

    lecturers = models.Lecturer.objects.filter(first_name=first_name)
    assert len(lecturers) == 0

    response = auth_client.post(
        "/dozenten/add/",
        {
            "title": "Dr",
            "last_name": "Einstein",
            "first_name": first_name,
            "abbreviation": "ale",
        },
    )
    print("response: ", response)
    lecturers = models.Lecturer.objects.filter(first_name=first_name)

    assert len(lecturers) == 1
    assert response.status_code == 302


def test_lecturer_add_button_available(auth_client):
    response = auth_client.get("/dozenten/")

    assert "Dozent hinzufügen" in response.content.decode("utf-8")


class QuoteAddViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe("apps.front.user")
        baker.make_recipe("apps.lecturers.lecturer")
        # setUp
        login(self)

    def testGenericForm(self):
        """Test the form that is shown if no lecturer is preselected."""
        response = self.client.get("/zitate/add/")
        self.assertContains(response, "<h1>Zitat hinzufügen</h1>")
        self.assertContains(response, '<option value="" selected>---------</option>')

    def testPrefilledForm(self):
        """Test the form that is shown if a lecturer is preselected."""
        response = self.client.get("/zitate/1337/add/")
        self.assertContains(response, "<h1>Zitat hinzufügen</h1>")
        self.assertContains(
            response, '<select name="lecturer" required id="id_lecturer">'
        )
        self.assertContains(
            response, '<option value="1337" selected>Krakaduku David</option>'
        )

    def testFormSubmission(self):
        """Test whether a quote submission gets saved correctly."""
        response = self.client.post(
            "/zitate/add/",
            {
                "lecturer": "1337",
                "quote": "ich bin der beste dozent von allen.",
                "comment": "etwas arrogant, nicht?",
            },
        )
        self.assertRedirects(response, "/zitate/")
        response2 = self.client.get("/zitate/")
        self.assertContains(response2, "<p>ich bin der beste dozent von allen.</p>")
        self.assertContains(response2, '<p class="comment">etwas arrogant, nicht?</p>')

    def testAutoUpvote(self):
        """Test whether the added quote was automatically upvoted."""
        self.client.post(
            "/zitate/add/",
            {
                "pk": 9000,
                "lecturer": "1337",
                "quote": "ich bin der töllscht!",
            },
        )
        quote = models.Quote.objects.get(lecturer=1337, quote="ich bin der töllscht!")
        assert quote.vote_sum() == 1, "Quote wasn't automatically upvoted..."


class QuoteViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe("apps.front.user")
        # setUp
        login(self)
        self.response = self.client.get("/zitate/")

    def testTitle(self):
        self.assertContains(self.response, "<h1>Zitate</h1>")

    def testQuoteInList(self):
        """Test whether an added quote shows up in the list."""
        baker.make(models.Quote, quote="spam", comment="ham")
        response = self.client.get("/zitate/")
        self.assertContains(response, "spam")
        self.assertContains(response, "ham")

    def testNullValueAuthor(self):
        """Test whether a quote without an author does not raise an error."""
        baker.make(models.Quote, quote="spam", comment="ham", author=None)
        response = self.client.get("/zitate/")
        self.assertContains(response, "spam")
        self.assertContains(response, "ham")


### Standardized listing tests (pytest style) ###


@pytest.mark.django_db
def test_lecturer_list_sort_links(auth_client):
    response = auth_client.get("/dozenten/")
    content = response.content.decode()
    assert 'href="?sort=name"' in content
    assert 'href="?sort=quotes"' in content


@pytest.mark.django_db
def test_lecturer_list_default_sort_by_name(auth_client):
    baker.make(models.Lecturer, first_name="Zoe", last_name="Zebra", abbreviation="zeb")
    baker.make(models.Lecturer, first_name="Amy", last_name="Apple", abbreviation="apl")
    response = auth_client.get("/dozenten/")
    content = response.content.decode()
    assert content.index("Apple") < content.index("Zebra")


@pytest.mark.django_db
def test_lecturer_list_sort_by_quote_count(auth_client, user):
    few_quotes = baker.make(
        models.Lecturer, first_name="Few", last_name="Quotes", abbreviation="few"
    )
    many_quotes = baker.make(
        models.Lecturer, first_name="Many", last_name="Quoted", abbreviation="many"
    )
    models.Quote.objects.create(author=user, lecturer=few_quotes, quote="a", comment="")
    for i in range(3):
        models.Quote.objects.create(
            author=user, lecturer=many_quotes, quote=f"b{i}", comment=""
        )
    response = auth_client.get("/dozenten/?sort=quotes")
    content = response.content.decode()
    assert content.index("Quoted") < content.index("Quotes")


@pytest.mark.django_db
def test_lecturer_list_quote_count_shown(auth_client, user):
    lecturer = baker.make(
        models.Lecturer, first_name="Cited", last_name="Prof", abbreviation="cited"
    )
    for i in range(3):
        models.Quote.objects.create(
            author=user, lecturer=lecturer, quote=f"q{i}", comment=""
        )
    response = auth_client.get("/dozenten/")
    assert "3 Zitate" in response.content.decode()


@pytest.mark.django_db
def test_quote_list_search_by_text(auth_client, user):
    lecturer = baker.make_recipe("apps.lecturers.lecturer")
    models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="Spam quote", comment=""
    )
    models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="Egg quote", comment=""
    )
    response = auth_client.get("/zitate/?q=spam")
    content = response.content.decode()
    assert "Spam quote" in content
    assert "Egg quote" not in content


@pytest.mark.django_db
def test_quote_list_search_by_lecturer_name(auth_client, user):
    krakaduku = baker.make_recipe("apps.lecturers.lecturer")
    other = baker.make(
        models.Lecturer, first_name="Xara", last_name="Yolo", abbreviation="xy"
    )
    models.Quote.objects.create(
        author=user, lecturer=krakaduku, quote="first q", comment=""
    )
    models.Quote.objects.create(
        author=user, lecturer=other, quote="second q", comment=""
    )
    response = auth_client.get("/zitate/?q=krakaduku")
    content = response.content.decode()
    assert "first q" in content
    assert "second q" not in content


@pytest.mark.django_db
def test_quote_list_default_sort_newest(auth_client, user):
    import datetime

    lecturer = baker.make_recipe("apps.lecturers.lecturer")
    old = models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="older one", comment=""
    )
    more_recent = models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="recent one", comment=""
    )
    models.Quote.objects.filter(pk=old.pk).update(
        date=datetime.datetime(2026, 1, 1, 12)
    )
    models.Quote.objects.filter(pk=more_recent.pk).update(
        date=datetime.datetime(2026, 1, 2, 12)
    )
    response = auth_client.get("/zitate/")
    content = response.content.decode()
    assert content.index("recent one") < content.index("older one")


@pytest.mark.django_db
def test_quote_list_sort_by_votes(auth_client, user):
    lecturer = baker.make_recipe("apps.lecturers.lecturer")
    other = User.objects.create_user(username="voter", password="t", email="voter@t.ch")
    unpopular = models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="unpopular q", comment=""
    )
    popular = models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="popular q", comment=""
    )
    models.QuoteVote.objects.create(user=user, quote=popular, vote=True)
    models.QuoteVote.objects.create(user=other, quote=popular, vote=True)
    models.QuoteVote.objects.create(user=user, quote=unpopular, vote=True)
    response = auth_client.get("/zitate/?sort=votes")
    content = response.content.decode()
    assert content.index("popular q") < content.index("unpopular q")


@pytest.mark.django_db
def test_quote_list_filter_by_lecturer(auth_client, user):
    l1 = baker.make_recipe("apps.lecturers.lecturer")
    l2 = baker.make(
        models.Lecturer, first_name="Xara", last_name="Yolo", abbreviation="xy"
    )
    models.Quote.objects.create(author=user, lecturer=l1, quote="l1 quote", comment="")
    models.Quote.objects.create(author=user, lecturer=l2, quote="l2 quote", comment="")
    response = auth_client.get("/zitate/", {"lecturer": l1.pk})
    content = response.content.decode()
    assert "l1 quote" in content
    assert "l2 quote" not in content
    # dropdown offers both lecturers
    assert f'value="{l2.pk}"' in content


@pytest.mark.django_db
def test_quote_list_invalid_filter_ignored(auth_client, user):
    lecturer = baker.make_recipe("apps.lecturers.lecturer")
    models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="some quote", comment=""
    )
    response = auth_client.get("/zitate/", {"lecturer": 99999})
    assert response.status_code == 200
    assert "some quote" in response.content.decode()


@pytest.mark.django_db
def test_quote_list_pagination_preserves_params(auth_client, user):
    lecturer = baker.make_recipe("apps.lecturers.lecturer")
    for i in range(55):
        models.Quote.objects.create(
            author=user, lecturer=lecturer, quote=f"paging quote {i:02d}", comment=""
        )
    response = auth_client.get("/zitate/", {"q": "paging", "sort": "date"})
    content = response.content.decode()
    assert 'class="pagination"' in content
    assert "?q=paging&amp;sort=date&amp;page=2" in content


@pytest.mark.django_db
def test_quote_rss_feed(client):
    """The quote feed is public and lists the newest quotes."""
    import datetime

    user = baker.make(User, username="quoter")
    lecturer = baker.make_recipe("apps.lecturers.lecturer")
    old = models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="older quote", comment="old comment"
    )
    new = models.Quote.objects.create(
        author=user, lecturer=lecturer, quote="newer quote", comment=""
    )
    models.Quote.objects.filter(pk=old.pk).update(
        date=datetime.datetime(2026, 1, 1, 12)
    )
    models.Quote.objects.filter(pk=new.pk).update(
        date=datetime.datetime(2026, 1, 2, 12)
    )
    response = client.get(reverse("lecturers:quote_feed"))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/rss+xml")
    content = response.content.decode("utf-8")
    assert "newer quote" in content
    assert "older quote" in content
    assert "old comment" in content
    assert f"#quote-{new.pk}" in content
    assert "newer quote" in content.split("older quote")[0]
