import atexit
import queue
import threading

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from apps.events import models

_STOP = object()
_CONCURRENCY = max(1, getattr(settings, "EVENT_NOTIFICATIONS_CONCURRENCY", 5))
_task_queue = queue.Queue()


def _worker():
    """Consume (user, event) tasks from the queue, one e-mail at a time."""
    while True:
        task = _task_queue.get()
        try:
            if task is _STOP:
                return
            user, event = task
            _send_event_email(user, event)
        finally:
            _task_queue.task_done()


for _ in range(_CONCURRENCY):
    # Daemon so the worker threads never keep the process alive at exit
    # (e.g. pytest teardown); atexit sentinels below drain best-effort.
    threading.Thread(target=_worker, daemon=True).start()


def _shutdown_workers():
    for _ in range(_CONCURRENCY):
        _task_queue.put(_STOP)


atexit.register(_shutdown_workers)


def flush():
    """Block until every queued notification has been sent.

    Lets callers (e.g. tests) wait for the buffered e-mails to actually be
    handed to the e-mail backend before asserting on the result.
    """
    _task_queue.join()


def send_event_notification(event):
    """Queue a notification e-mail to all opted-in users.

    One e-mail is sent per user (to all of their notification addresses) so
    that each user can be addressed by name.

    The e-mails are buffered in a task queue and processed by a bounded pool of
    worker threads, so only EVENT_NOTIFICATIONS_CONCURRENCY are in flight at
    once and a slow/unreachable recipient never blocks the others or the HTTP
    request.
    """
    if not getattr(settings, "EVENT_NOTIFICATIONS_ENABLED", True):
        return
    users = get_user_model().objects.filter(
        is_active=True, receive_event_notifications=True
    )
    for user in users:
        _task_queue.put((user, event))


def _send_event_email(user, event):
    """Send the notification to a single user. Failures are isolated so an
    unreachable address never affects any other user's e-mail."""
    recipients = user.notification_addresses()
    if not recipients:
        return
    context = {
        "user": user,
        "event": event,
        "event_url": "%s%s"
        % (settings.SITE_URL, reverse("events:event_detail", args=[event.pk])),
        "profile_url": "%s%s" % (settings.SITE_URL, reverse("profile")),
    }
    subject = render_to_string("events/event_notification_subject.txt", context)
    subject = "".join(subject.splitlines())
    body = render_to_string("events/event_notification.txt", context)
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
        )
    except Exception:
        pass


@receiver(post_save, sender=models.Event)
def event_created(sender, instance, created, **kwargs):
    if created:
        send_event_notification(instance)
