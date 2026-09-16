from django.conf import settings
from django.db import models

from apps.front.models import VotableModel, VoteModel


class Tipp(VotableModel):
    """A tipp topp tipp."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Tipp",
        null=True,
        on_delete=models.SET_NULL,
    )
    summary = models.CharField("Titel", max_length=64)
    description = models.TextField("Beschreibung")

    vote_relation = "TippVote"

    def __str__(self):
        return f"{self.summary}"


class TippVote(VoteModel):
    """Tipp votes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="TippVote",
        null=True,
        on_delete=models.SET_NULL,
    )
    tipp = models.ForeignKey(Tipp, related_name="TippVote", on_delete=models.CASCADE)

    def __str__(self):
        fmt_args = self.user.username, "up" if self.vote else "down", self.tipp.pk
        return "User %s votes %s tipp %s" % fmt_args

    class Meta:
        unique_together = ("user", "tipp")


class TippComment(models.Model):
    """A comment on a tipp."""

    tipp = models.ForeignKey(Tipp, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tipp_comments",
    )
    text = models.TextField("Kommentar")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Comment by {self.author} on Tipp {self.tipp_id}"
