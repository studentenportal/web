"""Shared voting helpers for votable content (quotes, tipps, etc.)."""

from django.db.models import (
    BooleanField,
    Count,
    Exists,
    IntegerField,
    OuterRef,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView


def _vote_count_subquery(vote_model, item_fk_name, vote=None, user_pk=None):
    """Correlated subquery counting votes of an item.

    Args:
        vote: True/False to restrict to upvotes/downvotes, None for all votes.
        user_pk: If given, only count this user's votes.
    """
    lookup = {item_fk_name: OuterRef("pk")}
    if vote is not None:
        lookup["vote"] = vote
    if user_pk is not None:
        lookup["user_id"] = user_pk
    subquery = (
        vote_model.objects.filter(**lookup)
        .values(item_fk_name)
        .annotate(count=Count("id"))
        .values("count")
    )
    return Coalesce(Subquery(subquery), Value(0), output_field=IntegerField())


def extend_with_votes(queryset, vote_model, item_fk_name, user_pk):
    """Extend a queryset with vote annotations using ORM subqueries.

    Args:
        queryset: The base queryset to annotate.
        vote_model: The vote model class (e.g. TippVote).
        item_fk_name: FK field name on the vote model pointing to the item
            (e.g. 'tipp').
        user_pk: The current user's PK, or None for anonymous users.

    The following annotations are added:
        vote_count: total number of votes for the item
        upvote_count: number of upvotes
        downvote_count: number of downvotes
        voted_up: whether the user has upvoted the item
        voted_down: whether the user has downvoted the item
    """
    if user_pk is None:
        voted_up = voted_down = Value(False, output_field=BooleanField())
    else:
        voted_up = Exists(
            vote_model.objects.filter(
                **{item_fk_name: OuterRef("pk"), "vote": True, "user_id": user_pk}
            )
        )
        voted_down = Exists(
            vote_model.objects.filter(
                **{item_fk_name: OuterRef("pk"), "vote": False, "user_id": user_pk}
            )
        )

    return queryset.annotate(
        vote_count=_vote_count_subquery(vote_model, item_fk_name),
        upvote_count=_vote_count_subquery(vote_model, item_fk_name, vote=True),
        downvote_count=_vote_count_subquery(vote_model, item_fk_name, vote=False),
        voted_up=voted_up,
        voted_down=voted_down,
    )


class VoteViewMixin(APIView):
    """Shared vote POST handler for votable models.

    Subclasses must set:
        item_model: The votable model class (e.g. Tipp, Quote)
        vote_model: The vote model class (e.g. TippVote, QuoteVote)
        item_fk_name: The FK field name on the vote model (e.g. 'tipp', 'quote')
    """

    item_model = None
    vote_model = None
    item_fk_name = None

    def post(self, request, pk):
        item = get_object_or_404(self.item_model, pk=pk)
        vote = request.POST.get("vote")

        if vote not in ["up", "down", "remove"]:
            return HttpResponseBadRequest("Expected up/down/remove for vote")

        lookup = {"user": request.user, self.item_fk_name: item}

        if vote == "remove":
            self.vote_model.objects.get(**lookup).delete()
        else:
            try:
                vote_obj = self.vote_model.objects.get(**lookup)
            except self.vote_model.DoesNotExist:
                vote_obj = self.vote_model(**lookup)
            vote_obj.vote = vote == "up"
            vote_obj.save()

        data = {
            "vote_elem_pk": item.pk,
            "vote": vote,
            "vote_count": getattr(item, item.vote_relation).count(),
            "vote_sum": item.vote_sum(),
        }
        return JsonResponse(data)
