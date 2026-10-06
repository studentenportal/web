import base64
import datetime
import json

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import BOUNDARY, encode_multipart
from django.urls import NoReverseMatch, reverse
from model_bakery import baker

from apps.documents import models as doc_models
from apps.events import models as event_models
from apps.lecturers.models import Lecturer, Quote, QuoteVote
from apps.tipps import models as tipp_models

User = get_user_model()


def make_pdf(name="test.pdf", content=b"%PDF-1.4 test"):
    return SimpleUploadedFile(name, content, content_type="application/pdf")


class TestAuthentication:
    def test_no_auth(self, client):
        """Test that requesting login-walled resources is not possible
        without auth (same as on the website)."""
        targets = [
            "user_list",
            "user_detail",
            "lecturer_list",
            "lecturer_detail",
            "quote_list",
            "quote_detail",
        ]
        for target in targets:
            try:
                url = reverse("api:" + target)
            except NoReverseMatch:
                url = reverse("api:" + target, args=(1,))
            resp = client.get(url)
            assert (
                resp.status_code == 401
            ), "Status code for %s is %d instead of 401." % (url, resp.status_code)
            assert resp.json() == {
                "detail": "Anmeldedaten fehlen.",
            }

    def test_anon_public_access(self, client, db):
        """Resources that are publicly visible on the website must be
        readable through the API without auth."""
        targets = [
            "api_root",
            "document_list",
            "documentcategory_list",
            "event_list",
            "tipp_list",
        ]
        for target in targets:
            url = reverse("api:" + target)
            resp = client.get(url)
            assert (
                resp.status_code == 200
            ), "Status code for %s is %d instead of 200." % (url, resp.status_code)

    def test_session_auth(self, auth_client):
        url = reverse("api:quote_list")
        resp = auth_client.get(url)
        assert resp.status_code == 200

    def test_basic_auth(self, client, user, db):
        url = reverse("api:quote_list")
        auth = b"Basic " + base64.b64encode(b"testuser:test")
        resp = client.get(url, HTTP_AUTHORIZATION=auth)
        assert resp.status_code == 200


class TestUserView:
    def test_status_code(self, user, auth_client):
        urls = [reverse("api:user_list"), reverse("api:user_detail", args=(user.pk,))]
        for url in urls:
            resp = auth_client.get(url)
            assert (
                resp.status_code == 200
            ), "Status code for %s is %d instead of 200." % (url, resp.status_code)

    def test_list_data(self, auth_client):
        users = [baker.make(User) for i in range(3)]
        url = reverse("api:user_list")
        resp = auth_client.get(url)
        data = resp.json()
        assert len(data["results"]) == data["count"]
        assert data["count"] == User.objects.count()

    def test_detail_data(self, user, auth_client):
        url = reverse("api:user_detail", args=(user.pk,))
        resp = auth_client.get(url)
        data = resp.json()
        attrs = ["id", "username", "first_name", "last_name", "email"]
        for attr in attrs:
            assert data[attr] == getattr(user, attr)

    def test_other_users_email_hidden(self, auth_client, db):
        """The email is sensitive data and only shown in one's own profile."""
        other_user = baker.make(User, username="otheruser")
        url = reverse("api:user_detail", args=(other_user.pk,))
        resp = auth_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "otheruser"
        assert "email" not in data

    def test_list_email_hidden(self, auth_client, db):
        baker.make(User, username="someuser", email="someuser@example.com")
        url = reverse("api:user_list")
        resp = auth_client.get(url)
        data = resp.json()
        assert all("email" not in item for item in data["results"])

    def test_list_methods(self, auth_client):
        url = reverse("api:user_list")
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "HEAD", "OPTIONS"}

    def test_detail_methods(self, user, auth_client):
        url = reverse("api:user_detail", args=(user.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "PUT", "HEAD", "OPTIONS", "PATCH"}

    def test_update_permissions(self, user, auth_client):
        """It should only be possible to edit own user."""
        another_user = baker.make(User)
        url1 = reverse("api:user_detail", args=(user.pk,))
        url2 = reverse("api:user_detail", args=(another_user.pk,))
        data1 = {"username": "test1", "email": "test1@example.com"}
        data2 = {"username": "test2", "email": "test2@example.com"}
        resp1 = auth_client.patch(url1, json.dumps(data1), "application/json")
        resp2 = auth_client.patch(url2, json.dumps(data2), "application/json")
        assert resp1.status_code == 200, resp1.content
        assert resp2.status_code == 403, resp2.content

    def test_username_change(self, user, auth_client):
        """You should not be able to change your own username."""
        url = reverse("api:user_detail", args=(user.pk,))
        data = {"username": "a_new_username", "email": user.email}
        resp = auth_client.patch(url, json.dumps(data), "application/json")
        assert resp.status_code == 200
        newuser = User.objects.get(pk=user.pk)
        assert user.username == newuser.username


class TestLecturerView:
    @pytest.fixture
    def lecturer(self, db):
        return baker.make(Lecturer)

    def test_status_code(self, lecturer, auth_client):
        urls = [
            reverse("api:lecturer_list"),
            reverse("api:lecturer_detail", args=(lecturer.pk,)),
        ]
        for url in urls:
            resp = auth_client.get(url)
            assert (
                resp.status_code == 200
            ), "Status code for %s is %d instead of 200." % (url, resp.status_code)

    def test_detail_data(self, lecturer, auth_client, db):
        [baker.make(Quote, lecturer=lecturer) for i in range(3)]

        url = reverse("api:lecturer_detail", args=(lecturer.pk,))
        resp = auth_client.get(url)
        data = resp.json()

        attrs = [
            "id",
            "title",
            "last_name",
            "first_name",
            "abbreviation",
            "department",
            "function",
            "main_area",
            "subjects",
            "email",
            "office",
        ]
        for attr in attrs:
            assert data[attr] == getattr(lecturer, attr)

        assert len(data["quotes"]) == lecturer.Quote.count()

    def test_list_methods(self, auth_client):
        url = reverse("api:lecturer_list")
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "HEAD", "OPTIONS"}

    def test_detail_methods(self, lecturer, auth_client):
        url = reverse("api:lecturer_detail", args=(lecturer.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "HEAD", "OPTIONS"}


class TestQuoteView:
    @pytest.fixture
    def quote(self, db, user):
        return baker.make(Quote, author=user)

    def test_status_code(self, auth_client, quote):
        urls = [
            reverse("api:quote_list"),
            reverse("api:quote_detail", args=(quote.pk,)),
        ]
        for url in urls:
            resp = auth_client.get(url)
            assert (
                resp.status_code == 200
            ), "Status code for %s is %d instead of 200." % (url, resp.status_code)

    def test_detail_data(self, auth_client, quote):
        url = reverse("api:quote_detail", args=(quote.pk,))
        resp = auth_client.get(url)
        data = resp.json()
        assert data["lecturer"] == quote.lecturer.pk
        assert data["lecturer_name"] == quote.lecturer.name()
        assert data["date"][:10] == quote.date.date().isoformat()
        assert data["comment"] == quote.comment

    def test_list_methods(self, auth_client):
        url = reverse("api:quote_list")
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "POST", "HEAD", "OPTIONS"}

    def test_detail_methods(self, auth_client, quote):
        url = reverse("api:quote_detail", args=(quote.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

    def test_delete_permissions(self, auth_client, user, quote, db):
        """It should only be possible to delete own quotes."""
        own_url = reverse("api:quote_detail", args=(quote.pk,))
        other_url = reverse("api:quote_detail", args=(baker.make(Quote).pk,))
        resp1 = auth_client.delete(own_url)
        resp2 = auth_client.delete(other_url)
        assert resp1.status_code == 204
        assert resp2.status_code == 403
        assert not Quote.objects.filter(pk=quote.pk).exists()
        assert Quote.objects.count() == 1

    def test_auto_author_POST(self, auth_client, user):
        """Assert that the author is automatically set to the currently logged
        in user on POST."""
        # Insert two quotes
        url = reverse("api:quote_list")
        lecturer = baker.make(Lecturer)
        other_user = baker.make(User)
        resp = auth_client.post(
            url,
            {
                "lecturer": lecturer.pk,
                "quote": "This is a test.",
                "comment": "No author",
            },
        )
        assert resp.status_code == 201
        resp = auth_client.post(
            url,
            {
                "lecturer": lecturer.pk,
                "author": other_user.pk,
                "quote": "This is a test.",
                "comment": "With author",
            },
        )
        assert resp.status_code == 201
        # Assert that two quotes were created.
        quote1 = Quote.objects.filter(comment="No author")
        quote2 = Quote.objects.filter(comment="With author")
        assert quote1.exists()
        assert quote2.exists()
        # Assert that the author is the currently logged in user
        assert quote1.get().author == user
        assert quote2.get().author == user

    def test_auto_author_PUT(self, auth_client, quote, user):
        """Assert that the author is automatically set to the currently logged
        in user on PUT."""
        # Update existing quote with new comment and author
        url = reverse("api:quote_detail", args=(quote.pk,))
        other_user = baker.make(User)
        data = {
            "lecturer": quote.lecturer.pk,
            "quote": quote.quote,
            "comment": "newcomment",
            "author": other_user.pk,
        }
        resp = auth_client.put(url, json.dumps(data), "application/json")
        # Assert that the PUT request was processed
        assert resp.status_code == 200
        # Comment should be changed, but not the author
        newquote = Quote.objects.get(pk=quote.pk)
        assert newquote.comment == "newcomment"
        assert newquote.author == user

    def test_update_permissions(self, auth_client, quote):
        """It should only be possible to edit own quotes."""
        quote2 = baker.make(Quote)
        url1 = reverse("api:quote_detail", args=(quote.pk,))
        url2 = reverse("api:quote_detail", args=(quote2.pk,))
        data = {
            "lecturer": quote.lecturer.pk,
            "quote": "testquote",
            "comment": "testcomment",
        }
        resp1 = auth_client.put(url1, json.dumps(data), "application/json")
        resp2 = auth_client.put(url2, json.dumps(data), "application/json")
        assert resp1.status_code == 200
        assert resp2.status_code == 403

    def test_author_change(self, auth_client, quote):
        """You should not be able to change the author of a quote."""
        url = reverse("api:quote_detail", args=(quote.pk,))
        another_user = baker.make(User)
        data = {
            "lecturer": quote.lecturer.pk,
            "quote": quote.quote,
            "comment": quote.comment,
            "author": another_user.pk,
        }
        resp = auth_client.put(url, json.dumps(data), "application/json")
        assert resp.status_code == 200, resp.content
        newquote = Quote.objects.get(pk=quote.pk)
        assert quote.author == newquote.author


class TestQuoteVote:
    @pytest.fixture
    def quote(self, db, user):
        return baker.make(Quote, author=user)

    @pytest.fixture
    def url(self, quote):
        return reverse("api:quote_vote", args=(quote.pk,))

    def test_login_required(self, client, url):
        """It shouldn't be possible to vote on a quote without login."""
        resp = client.post(url, {"vote": "up"})

        assert resp.status_code == 401
        assert resp.json() == {
            "detail": "Anmeldedaten fehlen.",
        }

    @pytest.fixture
    def voter(self, auth_client, url, quote):
        def _check_vote(vote, vote_count, vote_sum):
            resp = auth_client.post(url, {"vote": vote})
            assert resp.status_code == 200
            assert resp.json() == {
                "vote_elem_pk": quote.pk,
                "vote": vote,
                "vote_count": vote_count,
                "vote_sum": vote_sum,
            }
            assert QuoteVote.objects.count() == vote_count
            assert quote.vote_sum() == vote_sum

        return _check_vote

    def test_voting(self, voter):
        voter("down", 1, -1)
        voter("up", 1, 1)
        voter("remove", 0, 0)


class TestLecturerRate:
    @pytest.fixture
    def lecturer(self, db, user):
        return baker.make(Lecturer)

    @pytest.fixture
    def url(self, lecturer):
        return reverse("api:lecturer_rate", args=(lecturer.pk,))

    def test_login_required(self, client, url):
        """It shouldn't be possible to rate a lecturer without login."""
        resp = client.post(url, {"category": "d", "score": "5"})

        assert resp.status_code == 401
        assert resp.json() == {"detail": "Anmeldedaten fehlen."}

    @pytest.mark.parametrize(
        "data",
        [
            # Missing data
            {},
            {"category": "d"},
            {"score": "5"},
            # Invalid categories
            {"category": "donald", "score": 1},
            {"category": "x", "score": 1},
            {"category": "", "score": 1},
            # Invalid scores
            {"category": "d", "score": -1},
            {"category": "d", "score": 0},
            {"category": "d", "score": 11},
        ],
    )
    def test_invalid_data(self, data, auth_client, url):
        resp = auth_client.post(url, data)
        assert resp.status_code == 400
        assert resp.content == b"Validierungsfehler"

    @pytest.fixture
    def rater(self, auth_client, url):
        def _check_rating(category, score):
            data = {"category": category, "score": score}
            resp = auth_client.post(url, data)
            assert resp.status_code == 200
            assert resp.json() == {
                "category": category,
                "rating_count": 1,
                "rating_avg": score,
            }

        return _check_rating

    def test_rating(self, rater):
        rater("d", 5)
        rater("d", 4)
        rater("m", 6)
        rater("f", 10)


@pytest.mark.django_db
class TestApiListing:
    """Search and ordering of the API lists (standardized listing)."""

    def test_lecturer_search(self, auth_client):
        baker.make(
            Lecturer, first_name="David", last_name="Krakaduku", abbreviation="kra"
        )
        baker.make(
            Lecturer, first_name="Albert", last_name="Einstein", abbreviation="ein"
        )
        resp = auth_client.get(reverse("api:lecturer_list") + "?q=krakaduku")
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["last_name"] == "Krakaduku"

    def test_lecturer_ordering(self, auth_client):
        baker.make(Lecturer, last_name="Zebra", first_name="Z", abbreviation="zeb")
        baker.make(Lecturer, last_name="Alpha", first_name="A", abbreviation="alp")
        resp = auth_client.get(reverse("api:lecturer_list"))
        assert [r["last_name"] for r in resp.json()["results"]] == ["Alpha", "Zebra"]
        resp = auth_client.get(reverse("api:lecturer_list") + "?ordering=-last_name")
        assert [r["last_name"] for r in resp.json()["results"]] == ["Zebra", "Alpha"]

    def test_quote_search(self, auth_client):
        lecturer = baker.make(Lecturer, abbreviation="qte")
        baker.make(Quote, lecturer=lecturer, quote="spam quote")
        baker.make(Quote, lecturer=lecturer, quote="egg quote")
        resp = auth_client.get(reverse("api:quote_list") + "?q=spam")
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["quote"] == "spam quote"

    def test_user_search(self, auth_client):
        User.objects.create_user(username="alice", password="x", email="alice@t.ch")
        User.objects.create_user(username="bob", password="x", email="bob@t.ch")
        resp = auth_client.get(reverse("api:user_list") + "?q=alice")
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["username"] == "alice"

    def test_default_pagination(self, auth_client):
        for i in range(25):
            baker.make(Lecturer, last_name="Last%02d" % i, abbreviation="l%02d" % i)
        resp = auth_client.get(reverse("api:lecturer_list"))
        data = resp.json()
        assert data["count"] == 25
        assert len(data["results"]) == 20
        assert data["next"] is not None


class TestDocumentView:
    def test_anon_only_sees_public(self, client, db):
        public_doc = baker.make_recipe("apps.documents.document_summary", public=True)
        baker.make_recipe("apps.documents.document_exam")  # exams are non-public
        resp = client.get(reverse("api:document_list"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == public_doc.pk

    def test_anon_detail_visibility(self, client, db):
        public_doc = baker.make_recipe("apps.documents.document_summary", public=True)
        private_doc = baker.make_recipe("apps.documents.document_exam")
        assert (
            client.get(
                reverse("api:document_detail", args=(public_doc.pk,))
            ).status_code
            == 200
        )
        assert (
            client.get(
                reverse("api:document_detail", args=(private_doc.pk,))
            ).status_code
            == 404
        )

    def test_authed_sees_all(self, auth_client, db):
        baker.make_recipe("apps.documents.document_summary", public=True)
        baker.make_recipe("apps.documents.document_exam")
        data = auth_client.get(reverse("api:document_list")).json()
        assert data["count"] == 2

    def test_detail_data(self, auth_client, db):
        doc = baker.make_recipe(
            "apps.documents.document_summary",
            name="Zusammenfassung",
            description="Eine Zusammenfassung",
            license=3,
        )
        url = reverse("api:document_detail", args=(doc.pk,))
        resp = auth_client.get(url)
        data = resp.json()
        assert data["id"] == doc.pk
        assert data["name"] == doc.name
        assert data["description"] == doc.description
        assert data["dtype"] == doc.dtype
        assert data["license"] == doc.license
        assert data["public"] is False
        assert data["uploader"] == doc.uploader_id
        assert data["original_filename"] == doc.original_filename
        assert data["rating"] == 0
        assert data["rating_count"] == 0
        assert data["download_count"] == 0

    def test_list_methods(self, client, db):
        url = reverse("api:document_list")
        resp = client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "POST", "HEAD", "OPTIONS"}

    def test_detail_methods(self, auth_client, db):
        doc = baker.make_recipe("apps.documents.document_summary")
        url = reverse("api:document_detail", args=(doc.pk,))
        resp = auth_client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

    def test_create_requires_auth(self, client, db):
        category = baker.make(doc_models.DocumentCategory, name="CatA")
        resp = client.post(
            reverse("api:document_list"),
            {
                "name": "Test",
                "category": category.pk,
                "dtype": doc_models.Document.DTypes.SUMMARY,
                "document": make_pdf(),
            },
        )
        assert resp.status_code == 401

    def test_create(self, auth_client, user, db):
        category = baker.make(doc_models.DocumentCategory, name="CatB")
        resp = auth_client.post(
            reverse("api:document_list"),
            {
                "name": "Testdokument",
                "description": "Beschreibung",
                "category": category.pk,
                "dtype": doc_models.Document.DTypes.SUMMARY,
                "public": "true",
                "document": make_pdf("upload.pdf"),
            },
        )
        assert resp.status_code == 201, resp.content
        doc = doc_models.Document.objects.get(name="Testdokument")
        assert doc.uploader == user
        assert doc.category == category
        assert doc.public is True
        assert doc.original_filename == "upload.pdf"

    def test_create_exam_cannot_be_public(self, auth_client, db):
        category = baker.make(doc_models.DocumentCategory, name="CatC")
        resp = auth_client.post(
            reverse("api:document_list"),
            {
                "name": "Prüfung",
                "category": category.pk,
                "dtype": doc_models.Document.DTypes.EXAM,
                "public": "true",
                "document": make_pdf(),
            },
        )
        assert resp.status_code == 400
        assert not doc_models.Document.objects.filter(name="Prüfung").exists()

    def test_update_permissions(self, auth_client, user, db):
        own_doc = baker.make_recipe(
            "apps.documents.document_summary", uploader=user, name="Meine"
        )
        other_doc = baker.make_recipe("apps.documents.document_summary", name="Fremde")
        url1 = reverse("api:document_detail", args=(own_doc.pk,))
        url2 = reverse("api:document_detail", args=(other_doc.pk,))
        data = json.dumps({"name": "Neuer Name"})
        resp1 = auth_client.patch(url1, data, "application/json")
        resp2 = auth_client.patch(url2, data, "application/json")
        assert resp1.status_code == 200, resp1.content
        assert resp2.status_code == 403, resp2.content

    def test_update_reupload_changes_date(self, auth_client, user, db):
        doc = baker.make_recipe(
            "apps.documents.document_summary",
            uploader=user,
            name="Original",
        )
        old_change_date = datetime.datetime(2020, 1, 1, 12, 0, 0)
        doc.change_date = old_change_date
        doc.save()
        url = reverse("api:document_detail", args=(doc.pk,))
        body = encode_multipart(
            BOUNDARY, {"name": "Original", "document": make_pdf("neu.pdf")}
        )
        resp = auth_client.patch(
            url, body, content_type="multipart/form-data; boundary=%s" % BOUNDARY
        )
        assert resp.status_code == 200, resp.content
        doc.refresh_from_db()
        assert doc.change_date != old_change_date
        assert doc.original_filename == "neu.pdf"

    def test_delete_permissions(self, auth_client, user, db):
        own_doc = baker.make_recipe("apps.documents.document_summary", uploader=user)
        other_doc = baker.make_recipe("apps.documents.document_summary")
        url1 = reverse("api:document_detail", args=(own_doc.pk,))
        url2 = reverse("api:document_detail", args=(other_doc.pk,))
        resp1 = auth_client.delete(url1)
        resp2 = auth_client.delete(url2)
        assert resp1.status_code == 204
        assert resp2.status_code == 403
        assert not doc_models.Document.objects.filter(pk=own_doc.pk).exists()
        assert doc_models.Document.objects.filter(pk=other_doc.pk).exists()


class TestDocumentRate:
    @pytest.fixture
    def document(self, db):
        return baker.make_recipe("apps.documents.document_summary")

    @pytest.fixture
    def url(self, document):
        return reverse("api:document_rate", args=(document.pk,))

    def test_login_required(self, client, url):
        resp = client.post(url, {"score": "5"})
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Anmeldedaten fehlen."}

    def test_missing_score(self, auth_client, url):
        resp = auth_client.post(url, {})
        assert resp.status_code == 400

    def test_invalid_score(self, auth_client, url):
        resp = auth_client.post(url, {"score": "0"})
        assert resp.status_code == 400
        assert resp.content == b"Validierungsfehler"

    def test_own_upload_cannot_be_rated(self, auth_client, user, db):
        doc = baker.make_recipe("apps.documents.document_summary", uploader=user)
        url = reverse("api:document_rate", args=(doc.pk,))
        resp = auth_client.post(url, {"score": "5"})
        assert resp.status_code == 400
        assert resp.content == b"Validierungsfehler"

    def test_rating(self, auth_client, document, url):
        resp = auth_client.post(url, {"score": 5})
        assert resp.status_code == 200
        assert resp.json() == {"rating": 5, "rating_avg": 5, "rating_count": 1}
        # Updating the rating does not create a new one
        resp = auth_client.post(url, {"score": 8})
        assert resp.status_code == 200
        assert resp.json() == {"rating": 8, "rating_avg": 8, "rating_count": 1}
        assert doc_models.DocumentRating.objects.count() == 1


class TestDocumentCategoryView:
    def test_anon_access(self, client, db):
        category = baker.make(doc_models.DocumentCategory, name="CatD")
        assert client.get(reverse("api:documentcategory_list")).status_code == 200
        assert (
            client.get(
                reverse("api:documentcategory_detail", args=(category.pk,))
            ).status_code
            == 200
        )

    def test_detail_data(self, client, db):
        category = baker.make(
            doc_models.DocumentCategory, name="Prog3", description="Programmieren 3"
        )
        data = client.get(
            reverse("api:documentcategory_detail", args=(category.pk,))
        ).json()
        assert data == {
            "id": category.pk,
            "name": "Prog3",
            "description": "Programmieren 3",
        }

    def test_list_methods(self, client, db):
        url = reverse("api:documentcategory_list")
        resp = client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "POST", "HEAD", "OPTIONS"}

    def test_create_requires_auth(self, client, db):
        resp = client.post(
            reverse("api:documentcategory_list"),
            {"name": "CompT1", "description": "Computertechnik 1"},
        )
        assert resp.status_code == 401

    def test_create(self, auth_client, db):
        resp = auth_client.post(
            reverse("api:documentcategory_list"),
            {"name": "CompT1", "description": "Computertechnik 1"},
        )
        assert resp.status_code == 201, resp.content
        assert doc_models.DocumentCategory.objects.filter(name="CompT1").exists()


class TestEventView:
    @pytest.fixture
    def event(self, db, user):
        return baker.make(event_models.Event, author=user)

    def test_anon_access(self, client, event):
        assert client.get(reverse("api:event_list")).status_code == 200
        assert (
            client.get(reverse("api:event_detail", args=(event.pk,))).status_code == 200
        )

    def test_detail_data(self, client, event):
        data = client.get(reverse("api:event_detail", args=(event.pk,))).json()
        assert data["id"] == event.pk
        assert data["summary"] == event.summary
        assert data["description"] == event.description
        assert data["author"] == event.author_id

    def test_create_requires_auth(self, client, db):
        resp = client.post(
            reverse("api:event_list"),
            {
                "summary": "Test",
                "description": "Beschreibung",
                "start_date": "2026-11-05",
            },
        )
        assert resp.status_code == 401

    def test_create(self, auth_client, user, db):
        resp = auth_client.post(
            reverse("api:event_list"),
            {
                "summary": "Neues Event",
                "description": "Beschreibung",
                "start_date": "2026-11-05",
            },
        )
        assert resp.status_code == 201, resp.content
        event = event_models.Event.objects.get(summary="Neues Event")
        assert event.author == user

    def test_create_recurring_validation(self, auth_client, db):
        resp = auth_client.post(
            reverse("api:event_list"),
            {
                "summary": "Wiederholend",
                "description": "Beschreibung",
                "start_date": "2026-11-05",
                "repeats": "true",
            },
        )
        assert resp.status_code == 400
        assert not event_models.Event.objects.filter(summary="Wiederholend").exists()

    def test_list_methods(self, client, db):
        url = reverse("api:event_list")
        resp = client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "POST", "HEAD", "OPTIONS"}

    def test_update_permissions(self, auth_client, user, event, db):
        other_event = baker.make(event_models.Event)
        url1 = reverse("api:event_detail", args=(event.pk,))
        url2 = reverse("api:event_detail", args=(other_event.pk,))
        data = json.dumps({"summary": "Geändert"})
        resp1 = auth_client.patch(url1, data, "application/json")
        resp2 = auth_client.patch(url2, data, "application/json")
        assert resp1.status_code == 200, resp1.content
        assert resp2.status_code == 403, resp2.content

    def test_delete_permissions(self, auth_client, user, event, db):
        other_event = baker.make(event_models.Event)
        url1 = reverse("api:event_detail", args=(event.pk,))
        url2 = reverse("api:event_detail", args=(other_event.pk,))
        resp1 = auth_client.delete(url1)
        resp2 = auth_client.delete(url2)
        assert resp1.status_code == 204
        assert resp2.status_code == 403
        assert not event_models.Event.objects.filter(pk=event.pk).exists()


class TestTippView:
    @pytest.fixture
    def tipp(self, db, user):
        return baker.make(tipp_models.Tipp, author=user)

    def test_anon_access(self, client, tipp):
        assert client.get(reverse("api:tipp_list")).status_code == 200
        assert (
            client.get(reverse("api:tipp_detail", args=(tipp.pk,))).status_code == 200
        )

    def test_detail_data(self, client, tipp, db):
        tipp_models.TippComment.objects.create(
            tipp=tipp, author=tipp.author, text="Kommentar"
        )
        data = client.get(reverse("api:tipp_detail", args=(tipp.pk,))).json()
        assert data["id"] == tipp.pk
        assert data["summary"] == tipp.summary
        assert data["description"] == tipp.description
        assert data["author"] == tipp.author_id
        assert data["votes"] == 0
        assert data["comment_count"] == 1

    def test_create_requires_auth(self, client, db):
        resp = client.post(
            reverse("api:tipp_list"),
            {"summary": "Tipp", "description": "Beschreibung"},
        )
        assert resp.status_code == 401

    def test_create(self, auth_client, user, db):
        other_user = baker.make(User)
        resp = auth_client.post(
            reverse("api:tipp_list"),
            {
                "summary": "Neuer Tipp",
                "description": "Beschreibung",
                "author": other_user.pk,
            },
        )
        assert resp.status_code == 201, resp.content
        new_tipp = tipp_models.Tipp.objects.get(summary="Neuer Tipp")
        assert new_tipp.author == user

    def test_update_permissions(self, auth_client, user, tipp, db):
        other_tipp = baker.make(tipp_models.Tipp)
        url1 = reverse("api:tipp_detail", args=(tipp.pk,))
        url2 = reverse("api:tipp_detail", args=(other_tipp.pk,))
        data = json.dumps({"summary": "Geändert"})
        resp1 = auth_client.patch(url1, data, "application/json")
        resp2 = auth_client.patch(url2, data, "application/json")
        assert resp1.status_code == 200, resp1.content
        assert resp2.status_code == 403, resp2.content

    def test_delete_permissions(self, auth_client, user, tipp, db):
        other_tipp = baker.make(tipp_models.Tipp)
        url1 = reverse("api:tipp_detail", args=(tipp.pk,))
        url2 = reverse("api:tipp_detail", args=(other_tipp.pk,))
        resp1 = auth_client.delete(url1)
        resp2 = auth_client.delete(url2)
        assert resp1.status_code == 204
        assert resp2.status_code == 403
        assert not tipp_models.Tipp.objects.filter(pk=tipp.pk).exists()

    def test_list_methods(self, client, db):
        url = reverse("api:tipp_list")
        resp = client.head(url)
        allow = set(resp.get("Allow").split(", "))
        assert allow == {"GET", "POST", "HEAD", "OPTIONS"}


class TestTippVote:
    @pytest.fixture
    def tipp(self, db, user):
        return baker.make(tipp_models.Tipp, author=user)

    @pytest.fixture
    def url(self, tipp):
        return reverse("api:tipp_vote", args=(tipp.pk,))

    def test_login_required(self, client, url):
        resp = client.post(url, {"vote": "up"})
        assert resp.status_code == 401
        assert resp.json() == {"detail": "Anmeldedaten fehlen."}

    def test_voting(self, auth_client, url, tipp):
        def _check_vote(vote, vote_count, vote_sum):
            resp = auth_client.post(url, {"vote": vote})
            assert resp.status_code == 200
            assert resp.json() == {
                "vote_elem_pk": tipp.pk,
                "vote": vote,
                "vote_count": vote_count,
                "vote_sum": vote_sum,
            }
            assert tipp_models.TippVote.objects.count() == vote_count
            assert tipp.vote_sum() == vote_sum

        _check_vote("up", 1, 1)
        _check_vote("down", 1, -1)
        _check_vote("remove", 0, 0)


class TestTippComment:
    @pytest.fixture
    def tipp(self, db, user):
        return baker.make(tipp_models.Tipp, author=user)

    @pytest.fixture
    def list_url(self, tipp):
        return reverse("api:tipp_comment_list", args=(tipp.pk,))

    @pytest.fixture
    def comment(self, db, user, tipp):
        return tipp_models.TippComment.objects.create(
            tipp=tipp, author=user, text="Mein Kommentar"
        )

    def test_anon_list(self, client, tipp, list_url, comment):
        resp = client.get(list_url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["text"] == "Mein Kommentar"
        assert data["results"][0]["author"] == comment.author_id

    def test_create_requires_auth(self, client, list_url):
        resp = client.post(list_url, {"text": "Kommentar"})
        assert resp.status_code == 401

    def test_create(self, auth_client, user, tipp, list_url):
        resp = auth_client.post(list_url, {"text": "Kommentar"})
        assert resp.status_code == 201, resp.content
        comment = tipp_models.TippComment.objects.get(text="Kommentar")
        assert comment.tipp == tipp
        assert comment.author == user

    def test_scoped_to_tipp(self, client, tipp, list_url, db):
        other_tipp = baker.make(tipp_models.Tipp)
        other_comment = tipp_models.TippComment.objects.create(
            tipp=other_tipp, text="Fremder Kommentar"
        )
        url = reverse("api:tipp_comment_detail", args=(tipp.pk, other_comment.pk))
        assert client.get(url).status_code == 404
        assert client.get(list_url).json()["count"] == 0

    def test_update_permissions(self, auth_client, user, tipp, comment, db):
        other_comment = tipp_models.TippComment.objects.create(
            tipp=tipp, text="Fremder Kommentar"
        )
        url1 = reverse("api:tipp_comment_detail", args=(tipp.pk, comment.pk))
        url2 = reverse("api:tipp_comment_detail", args=(tipp.pk, other_comment.pk))
        data = json.dumps({"text": "Geändert"})
        resp1 = auth_client.patch(url1, data, "application/json")
        resp2 = auth_client.patch(url2, data, "application/json")
        assert resp1.status_code == 200, resp1.content
        assert resp2.status_code == 403, resp2.content

    def test_delete_permissions(self, auth_client, user, tipp, comment, db):
        other_comment = tipp_models.TippComment.objects.create(
            tipp=tipp, text="Fremder Kommentar"
        )
        url1 = reverse("api:tipp_comment_detail", args=(tipp.pk, comment.pk))
        url2 = reverse("api:tipp_comment_detail", args=(tipp.pk, other_comment.pk))
        assert auth_client.delete(url1).status_code == 204
        assert auth_client.delete(url2).status_code == 403
        assert not tipp_models.TippComment.objects.filter(pk=comment.pk).exists()
