import re
import uuid
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from model_bakery import baker

from apps.front.models import InactivityNotice

User = get_user_model()


def make_user(username, last_login=None, date_joined=None):
    return baker.make(
        User,
        username=username,
        email=f"{username}@ost.ch",
        last_login=last_login,
        date_joined=date_joined or timezone.now(),
    )


@pytest.fixture(autouse=True)
def clear_mail():
    mail.outbox.clear()
    yield


@pytest.mark.django_db
def test_notify_inactive_users():
    """Inactive users get a confirmation e-mail with a working link."""
    now = timezone.now()
    make_user("active.user", last_login=now - timedelta(days=1))
    inactive = make_user("inactive.user", last_login=now - timedelta(days=400))
    never_logged_in = make_user(
        "never.user", last_login=None, date_joined=now - timedelta(days=400)
    )
    fresh = make_user(
        "fresh.user", last_login=None, date_joined=now - timedelta(days=1)
    )

    call_command("notify_inactive_users")

    notified = {message.to[0] for message in mail.outbox}
    assert notified == {"inactive.user@ost.ch", "never.user@ost.ch"}
    assert InactivityNotice.objects.filter(user=inactive).count() == 1
    assert InactivityNotice.objects.filter(user=never_logged_in).count() == 1
    active_user = User.objects.get(username="active.user")
    assert InactivityNotice.objects.filter(user=active_user).count() == 0
    assert InactivityNotice.objects.filter(user=fresh).count() == 0


@pytest.mark.django_db
def test_notify_inactive_users_link_confirms(client):
    """The link in the notification e-mail confirms the notice."""
    now = timezone.now()
    make_user("inactive.user", last_login=now - timedelta(days=400))
    call_command("notify_inactive_users")

    body = mail.outbox[0].body
    match = re.search(r"/accounts/confirm-active/([0-9a-f]{32})/", body)
    assert match is not None
    token = match.group(1)
    response = client.get(f"/accounts/confirm-active/{token}/")
    assert response.status_code == 200
    assert "wurde bestätigt" in response.content.decode("utf-8")
    assert InactivityNotice.objects.filter(
        token=token, confirmed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_notify_skips_users_with_pending_notice():
    """No second e-mail while a notice is still pending."""
    now = timezone.now()
    user = make_user("pending.user", last_login=now - timedelta(days=400))
    InactivityNotice.objects.create(user=user, token=uuid.uuid4().hex)

    call_command("notify_inactive_users")

    assert mail.outbox == []
    assert user.inactivity_notices.count() == 1


@pytest.mark.django_db
def test_purge_deletes_unconfirmed_inactive_users():
    now = timezone.now()
    doomed = make_user("doomed.user", last_login=now - timedelta(days=400))
    notice = InactivityNotice.objects.create(user=doomed, token=uuid.uuid4().hex)
    InactivityNotice.objects.filter(pk=notice.pk).update(
        sent_at=now - timedelta(days=100)
    )

    call_command("purge_inactive_users")

    assert not User.objects.filter(username="doomed.user").exists()


@pytest.mark.django_db
def test_purge_keeps_confirmed_users():
    now = timezone.now()
    user = make_user("confirmed.user", last_login=now - timedelta(days=400))
    notice = InactivityNotice.objects.create(user=user, token=uuid.uuid4().hex)
    notice.sent_at = now - timedelta(days=100)
    notice.confirmed_at = now - timedelta(days=99)
    notice.save()

    call_command("purge_inactive_users")

    assert User.objects.filter(username="confirmed.user").exists()


@pytest.mark.django_db
def test_purge_keeps_recently_active_users():
    """A user that logged in after the notice was sent is kept."""
    now = timezone.now()
    user = make_user("cameback.user", last_login=now - timedelta(days=400))
    InactivityNotice.objects.create(user=user, token=uuid.uuid4().hex)
    InactivityNotice.objects.filter(user=user).update(sent_at=now - timedelta(days=100))
    user.last_login = now - timedelta(days=1)
    user.save()

    call_command("purge_inactive_users")

    assert User.objects.filter(username="cameback.user").exists()


@pytest.mark.django_db
def test_purge_keeps_fresh_notices():
    """Notices that are still within the confirmation period are kept."""
    now = timezone.now()
    user = make_user("freshnotice.user", last_login=now - timedelta(days=400))
    InactivityNotice.objects.create(user=user, token=uuid.uuid4().hex)

    call_command("purge_inactive_users")

    assert User.objects.filter(username="freshnotice.user").exists()
