from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class VotableModel(models.Model):
    """Abstract base for models that can be voted on (quotes, tipps, etc.).

    Subclasses must define:
        - author FK (with their own related_name)
        - vote_relation: the related_name of the vote FK pointing here
    """

    date = models.DateTimeField(auto_now_add=True)

    # Subclasses must set this to the related_name of the vote FK pointing here
    vote_relation = None

    def date_available(self):
        return self.date != datetime(1970, 1, 1)

    def vote_sum(self):
        """Add up and return all votes for this item."""
        related_manager = getattr(self, self.vote_relation)
        up = related_manager.filter(vote=True).count()
        down = related_manager.filter(vote=False).count()
        return up - down

    class Meta:
        abstract = True
        ordering = ["-date"]
        get_latest_by = "date"


class VoteModel(models.Model):
    """Abstract base for vote models (QuoteVote, TippVote, etc.).

    Subclasses must define:
        - user FK (with their own related_name)
        - FK to the votable item
    """

    vote = models.BooleanField(help_text="True = upvote, False = downvote")

    class Meta:
        abstract = True


def strip_mail_part(username):
    """
    Users might try to login with their email. To support that
    we can simply strip the mail part from the username
    """
    if "@" in username:
        return username.split("@")[0]
    return username


class CustomUserManager(UserManager):
    """
    By default, django.contrib.auth does case _sensitive_ username authentication, which isn't what is
    generally expected. By defining a custom user manager, we can compare user
    names case insensitively and strip off the email part.

    Sources:

    https://djangosnippets.org/snippets/1368/
    https://code.djangoproject.com/ticket/2273#comment:12
    """

    def get_by_natural_key(self, username):
        username = strip_mail_part(username)
        return self.get(username__iexact=username)


class User(AbstractUser):
    """The user model."""

    users = CustomUserManager()

    notification_email = models.EmailField(
        "Zusätzliche E-Mail-Adresse",
        blank=True,
        default="",
        max_length=254,
        help_text="Optionale zweite Adresse, an die Benachrichtigungen zusätzlich gesendet werden.",
    )
    receive_event_notifications = models.BooleanField(
        "Neue Events per E-Mail",
        default=True,
        help_text="Ob du eine E-Mail erhalten möchtest, wenn ein neues Event erfasst wird.",
    )

    def name(self):
        """Return either full user first and last name or the username, if no
        further data is found."""
        if self.first_name or self.last_name:
            return " ".join(part for part in [self.first_name, self.last_name] if part)
        return self.username

    def notification_addresses(self):
        """All e-mail addresses of this user that should receive
        notifications (main address plus the optional additional one),
        lowercased and de-duplicated."""
        addresses = []
        for address in (self.email, self.notification_email):
            if address and address.lower() not in addresses:
                addresses.append(address.lower())
        return addresses


class InactivityNotice(models.Model):
    """A confirmation request sent to an inactive user.

    The user has to confirm the account by following the link in the e-mail
    (see `notify_inactive_users` / `purge_inactive_users`).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inactivity_notices",
    )
    token = models.CharField(max_length=64, unique=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    def confirmation_url(self):
        from django.conf import settings as django_settings

        from django.urls import reverse

        return "%s%s" % (
            django_settings.SITE_URL,
            reverse("confirm_active", args=[self.token]),
        )
