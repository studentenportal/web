import pytest
from django.contrib.auth import get_user_model

from apps.tipps.models import Tipp, TippComment

User = get_user_model()


@pytest.mark.django_db
class TestTippComment:
    def test_create_comment(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Nice tipp!")
        assert comment.pk is not None
        assert comment.text == "Nice tipp!"
        assert comment.tipp == tipp
        assert comment.author == user

    def test_comment_ordering_oldest_first(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        c1 = TippComment.objects.create(tipp=tipp, author=user, text="First")
        c2 = TippComment.objects.create(tipp=tipp, author=user, text="Second")
        comments = list(tipp.comments.all())
        assert comments == [c1, c2]

    def test_comment_cascade_delete(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        TippComment.objects.create(tipp=tipp, author=user, text="Comment")
        assert TippComment.objects.count() == 1
        tipp.delete()
        assert TippComment.objects.count() == 0

    def test_comment_author_set_null(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Comment")
        user.delete()
        comment.refresh_from_db()
        assert comment.author is None

    def test_str(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Comment")
        assert "testuser" in str(comment)
        assert str(tipp.pk) in str(comment)
