import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from apps.front.models import InactivityNotice


class Command(BaseCommand):
    help = (
        "Send a confirmation e-mail to users that haven't logged in for a while "
        "(see INACTIVITY_NOTICE_THRESHOLD_DAYS). Users that didn't confirm within "
        "INACTIVITY_CONFIRMATION_PERIOD_DAYS are deleted by `purge_inactive_users`. "
        "Run periodically (e.g. daily via cron)."
    )

    def handle(self, *args, **options):
        User = get_user_model()
        now = timezone.now()
        cutoff = now - timedelta(days=settings.INACTIVITY_NOTICE_THRESHOLD_DAYS)
        users = User.objects.filter(is_active=True).filter(
            Q(last_login__lt=cutoff)
            | (Q(last_login__isnull=True) & Q(date_joined__lt=cutoff))
        )
        sent = 0
        for user in users:
            if user.inactivity_notices.filter(confirmed_at__isnull=True).exists():
                continue
            notice = InactivityNotice.objects.create(user=user, token=uuid.uuid4().hex)
            context = {
                "user": user,
                "threshold_days": settings.INACTIVITY_NOTICE_THRESHOLD_DAYS,
                "confirmation_days": settings.INACTIVITY_CONFIRMATION_PERIOD_DAYS,
                "confirm_url": notice.confirmation_url(),
            }
            subject = render_to_string("front/inactivity_notice_subject.txt", context)
            subject = "".join(subject.splitlines())
            body = render_to_string("front/inactivity_notice.txt", context)
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            sent += 1
        self.stdout.write(self.style.SUCCESS("Sent %d inactivity notice(s)." % sent))
