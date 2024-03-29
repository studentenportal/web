import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertRedirects

User = get_user_model()


def login(self):
    assert self.client.login(username="testuser", password="test")


@pytest.mark.django_db
def test_home_view(client):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_view_unauth_redirect(client):
    """An unauthenticated user should not get access to the profile detail page."""
    response = client.get("/profil/")
    assert response.status_code == 302


class LoginTest(TestCase):
    url = "/accounts/login/"

    def setUp(self):
        # setUpClass
        baker.make_recipe("apps.front.user")

    def testTitle(self):
        r = self.client.get(self.url)
        self.assertContains(r, "<h1>Login</h1>")

    def testLogin(self):
        r1 = self.client.get("/zitate/")
        assert r1.status_code == 302
        login(self)
        r2 = self.client.get("/zitate/")
        assert r2.status_code == 200

    def testCaseInsensitveLogin(self):
        r1 = self.client.post(self.url, {"username": "testuser", "password": "test"})
        assert r1.status_code == 302
        r2 = self.client.post(self.url, {"username": "Testuser", "password": "test"})
        assert r2.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_registration(client):
    """
    Test that a registration is successful and that an activation email is
    sent.

    Needs to use a transaction because the mail is sent on on_commit.
    """
    registration_url = "/accounts/register/"

    response = client.post(
        registration_url,
        {
            "email": "test.user@ost.ch",
            "password1": "testpass",
            "password2": "testpass",
        },
    )
    assertRedirects(response, "/accounts/register/complete/")
    assert User.objects.filter(username="test.user").exists()

    transaction.commit()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "[studentenportal.ch] Aktivierung"


class RegistrationViewTest:
    registration_url = "/accounts/register/"

    def testRegistrationPage(self):
        response = client.get(self.registration_url)
        self.assertContains(response, "<h1>Registrieren</h1>")
        self.assertContains(
            response,
            "Diese Registrierung ist Studenten mit einer OST-Email-Adresse",
        )
        self.assertContains(response, "<form")

    def testRegistrationBadUsername(self, client):
        """
        Test that a registration with a bad username returns an error.
        """
        response = client.post(
            self.registration_url,
            {
                "email": "a.+++@ost.ch",
                "password1": "testpass",
                "password2": "testpass",
            },
        )
        assert response.status_code == 200
        content = response.content.decode("utf8")
        assert "Ungültige E-Mail" in content

    def testRegistrationLongUsernameOst(self, client):
        """
        Test that a registration with a long OST username works.
        """
        response = client.post(
            self.registration_url,
            {
                "email": "foo.bar@ost.ch",
                "password1": "testpass",
                "password2": "testpass",
            },
        )
        assert response.status_code == 302

    def testRegistrationShortUsernameOst(self, client):
        """
        Test that a registration with a short OST username fails.
        """
        response = client.post(
            self.registration_url,
            {
                "email": "foobar@ost.ch",
                "password1": "testpass",
                "password2": "testpass",
            },
        )
        assert response.status_code == 200
        content = response.content.decode("utf8")
        assert "Ungültige E-Mail" in content

    @pytest.mark.parametrize("domain", ["zhaw.ch", "hsr.ch"])
    def testRegistrationBadDomain(self, client, domain):
        """
        Test that a registration with a non-ost.ch Domain return an error.
        """
        response = client.post(
            self.registration_url,
            {
                "email": f"a.meier@{domain}",
                "password1": "testpass",
                "password2": "testpass",
            },
        )
        assert response.status_code == 200
        assert (
            "Registrierung ist Studierenden mit einer @ost.ch-Mailadresse vorbehalten"
            in response.content.decode("utf8")
        )

    def testRegistrationDoubleUsername(self, client):
        """
        Test that a registration with a duplicate username returns an error.
        """
        baker.make(User, username="a.b", email="a.b@ost.ch")
        response = client.post(
            self.registration_url,
            {
                "email": "a.b@ost.ch",
                "password1": "testpass",
                "password2": "testpass",
            },
        )
        assert response.status_code == 200
        assert "Benutzer &quot;a.b&quot; existiert bereits" in response.content.decode(
            "utf8"
        )

    def testRegistrationDoubleEmail(self, client):
        """
        Test that a registration with a duplicate email returns an error.
        """
        baker.make(User, username="abc", email="a.b.c@ost.ch")
        response = client.post(
            self.registration_url,
            {
                "email": "a.b.c@ost.ch",
                "password1": "testpass",
                "password2": "testpass",
            },
        )
        assert response.status_code == 200
        assert (
            "Benutzer mit dieser E-Mail existiert bereits."
            in response.content.decode("utf8")
        )


class UserViewTest(TestCase):
    def setUp(self):
        # setUpClass
        self.user1 = baker.make_recipe("apps.front.user")
        self.user2 = baker.make(
            User,
            first_name="Another",
            last_name="Guy",
            email="test2@studentenportal.ch",
        )
        self.doc1 = baker.make_recipe(
            "apps.documents.document_summary",
            name="Document 1",
            description="The first document.",
            uploader=self.user1,
            document="a.pdf",
        )
        self.doc2 = baker.make_recipe(
            "apps.documents.document_summary",
            name="Document 2",
            description="The second document.",
            uploader=self.user2,
            document="b.pdf",
        )
        # setUp
        login(self)

    def testOwnUserView(self):
        url = reverse("user", args=(self.user1.pk, self.user1.username))
        response = self.client.get(url)
        self.assertContains(response, "<h1>testuser</h1>")
        self.assertContains(response, "test@studentenportal.ch")

    def testOtherUserView(self):
        url = reverse("user", args=(self.user2.pk, self.user2.username))
        response = self.client.get(url)
        self.assertContains(response, "<h1>Another Guy</h1>")
        self.assertContains(response, "test2@studentenportal.ch")

    def testOwnDocuments(self):
        url = reverse("user", args=(self.user1.pk, self.user1.username))
        category = self.doc1.category.name
        response = self.client.get(url)
        # Own document should be listed
        self.assertContains(response, f'property="dct:title">{self.doc1.name}</h3>')
        # Foreign document should not be listed
        self.assertNotContains(response, f'property="dct:title">{self.doc2.name}</h3>')
        # Category should be displayed
        self.assertContains(response, f"{category}</span>")

    def testOtherDocuments(self):
        url = reverse("user", args=(self.user2.pk, self.user2.username))
        category = self.doc2.category.name
        response = self.client.get(url)
        # Own document should be listed
        self.assertContains(response, f'property="dct:title">{self.doc2.name}</h3>')
        # Foreign document should not be listed
        self.assertNotContains(response, f'property="dct:title">{self.doc1.name}</h3>')
        # Category should be displayed
        self.assertContains(response, f"{category}</span>")


class UserProfileViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe("apps.front.user")
        # setUp
        login(self)

    def testFormSubmission(self):
        """Test whether a profile form submission gets saved correctly."""
        response = self.client.post(
            "/profil/",
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        self.assertRedirects(response, "/profil/")
        user = User.objects.get(username="testuser")
        assert user.email == "test@studentenportal.ch"  # No change!
        assert user.first_name == "John"
        assert user.last_name == "Doe"


class StatsViewTest(TestCase):
    taburl = "/statistiken/"

    def setUp(self):
        # setUpClass
        baker.make_recipe("apps.front.user")

    def testLoginRequired(self):
        response = self.client.get(self.taburl)
        self.assertRedirects(response, "/accounts/login/?next=/statistiken/")

    def testTitle(self):
        login(self)
        response = self.client.get(self.taburl)
        self.assertContains(response, "<h1>Statistiken</h1>")
