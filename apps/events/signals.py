from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from apps.events import models


def send_event_notification(event):
    """Send a notification e-mail about a new event to all opted-in users.

    One e-mail is sent per user (to all of their notification addresses) so
    that each user can be addressed by name.
    """
    if not getattr(settings, "EVENT_NOTIFICATIONS_ENABLED", True):
        return
    User = get_user_model()
    users = User.objects.filter(is_active=True, receive_event_notifications=True)
    for user in users:
        recipients = user.notification_addresses()
        if not recipients:
            continue
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
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True,
        )


@receiver(post_save, sender=models.Event)
def event_created(sender, instance, created, **kwargs):
    if created:
        send_event_notification(instance)
