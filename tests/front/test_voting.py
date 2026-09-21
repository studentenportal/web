import pytest
from django.contrib.auth import get_user_model
from django.db.models import F

from apps.front.voting import extend_with_votes
from apps.tipps.models import Tipp, TippVote

User = get_user_model()


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="other", password="test", email="other@t.ch"
    )


@pytest.mark.django_db
def test_vote_counts(user, other_user):
    third = User.objects.create_user(
        username="third", password="test", email="third@t.ch"
    )
    popular = Tipp.objects.create(author=user, summary="Popular", description="d")
    quiet = Tipp.objects.create(author=user, summary="Quiet", description="d")
    TippVote.objects.create(user=user, tipp=popular, vote=True)
    TippVote.objects.create(user=other_user, tipp=popular, vote=True)
    TippVote.objects.create(user=third, tipp=popular, vote=False)

    qs = extend_with_votes(Tipp.objects.all(), TippVote, "tipp", user.pk)
    items = {t.summary: t for t in qs}
    assert items["Popular"].upvote_count == 2
    assert items["Popular"].downvote_count == 1
    assert items["Popular"].vote_count == 3
    assert items["Quiet"].upvote_count == 0
    assert items["Quiet"].downvote_count == 0
    assert items["Quiet"].vote_count == 0


@pytest.mark.django_db
def test_voted_up_down_flags(user, other_user):
    upped = Tipp.objects.create(author=user, summary="Up", description="d")
    downed = Tipp.objects.create(author=user, summary="Down", description="d")
    neutral = Tipp.objects.create(author=user, summary="Neutral", description="d")
    TippVote.objects.create(user=user, tipp=upped, vote=True)
    TippVote.objects.create(user=user, tipp=downed, vote=False)
    TippVote.objects.create(user=other_user, tipp=neutral, vote=True)

    qs = extend_with_votes(Tipp.objects.all(), TippVote, "tipp", user.pk)
    items = {t.summary: t for t in qs}
    assert items["Up"].voted_up is True
    assert items["Up"].voted_down is False
    assert items["Down"].voted_down is True
    assert items["Neutral"].voted_up is False
    assert items["Neutral"].voted_down is False


@pytest.mark.django_db
def test_anonymous_user_flags_false(user):
    tipp = Tipp.objects.create(author=user, summary="Public", description="d")
    TippVote.objects.create(user=user, tipp=tipp, vote=True)

    items = {
        t.summary: t
        for t in extend_with_votes(Tipp.objects.all(), TippVote, "tipp", None)
    }
    assert items["Public"].voted_up is False
    assert items["Public"].voted_down is False
    assert items["Public"].vote_count == 1


@pytest.mark.django_db
def test_vote_sum_expression_orderable(user, other_user):
    """Annotations must be usable in F() expressions in order_by."""
    other = other_user
    low = Tipp.objects.create(author=user, summary="Low", description="d")
    high = Tipp.objects.create(author=user, summary="High", description="d")
    TippVote.objects.create(user=user, tipp=high, vote=True)
    TippVote.objects.create(user=other, tipp=high, vote=True)
    TippVote.objects.create(user=user, tipp=low, vote=False)

    ordered = extend_with_votes(Tipp.objects.all(), TippVote, "tipp", user.pk).order_by(
        -(F("upvote_count") - F("downvote_count"))
    )
    assert [t.summary for t in ordered] == ["High", "Low"]
